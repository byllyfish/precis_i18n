"""Run local qualification without changing the upstream CI."""

import os
import shutil
from pathlib import Path

import nox

ROOT = Path(__file__).resolve().parent
PYTHONS = (
    "3.7", "3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "3.14", "3.15",
    "pypy3.10", "pypy3.11",
)

nox.options.sessions = ["tests"]
nox.options.error_on_missing_interpreters = True


def _report(session, kind):
    supplied = os.environ.get("PRECIS_QUALIFICATION_DIR")
    if not supplied:
        return []
    results = Path(supplied).resolve() / "results"
    results.mkdir(parents=True, exist_ok=True)
    return ["--junitxml", str(results / f"{kind}-{session.python}.xml")]


def _install_tools(session):
    session.install("pytest==7.4.4")
    _install_provider(session)


def _install_provider(session, *, required=False):
    provider_lock = os.environ.get("PRECIS_PROVIDER_LOCK")
    if provider_lock:
        wheelhouse = os.environ.get("PRECIS_PROVIDER_WHEELHOUSE")
        if not wheelhouse:
            session.error("Provide the pinned Unicode provider wheelhouse.")
        session.install(
            "--no-index", "--only-binary=:all:", "--no-deps", "--require-hashes",
            "--find-links", str(Path(wheelhouse).resolve()), "-r", str(Path(provider_lock).resolve()),
        )
    elif required:
        session.error("Provide a hash-locked Unicode provider for this session.")


@nox.session(python=PYTHONS)
def tests(session):
    """Run the upstream suite and correction tests from source."""
    _install_tools(session)
    session.chdir(str(ROOT))
    session.run(
        "python", "-I", "-c",
        "import sys, pytest; sys.path.insert(0, sys.argv.pop(1)); "
        "raise SystemExit(pytest.main(sys.argv[1:]))",
        str(ROOT), "-ra",
        *_report(session, "source"), *(session.posargs or ["test"]),
        env={"PYTEST_ADDOPTS": "", "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
    )


def _artifacts():
    value = os.environ.get("PRECIS_QUALIFICATION_DIR")
    if value:
        return Path(value).resolve() / "artifacts"
    return ROOT / "dist"


@nox.session(python="3.10")
def build(session):
    """Build and compare a direct wheel and a wheel from the canonical sdist."""
    session.install("build==1.3.0", "setuptools==80.9.0", "wheel==0.45.1")
    epoch = os.environ.get("SOURCE_DATE_EPOCH", "946684800")
    environment = {"SOURCE_DATE_EPOCH": epoch}
    # setuptools includes generated metadata file modes in wheel headers.
    builder = (
        "python", "-I", "-c",
        "import os, runpy; os.umask(0o022); runpy.run_module('build', run_name='__main__')",
    )
    output = _artifacts()
    staging = Path(session.create_tmp()).resolve() / "build"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir()
    for kind in ("direct", "source"):
        (output / kind).mkdir(parents=True, exist_ok=True)
    session.chdir(str(ROOT))
    session.run(*builder, "--no-isolation", "--sdist", "--outdir", str(staging), env=environment)
    (raw,) = staging.glob("*.tar.gz")
    sdist = output / "source" / raw.name
    helper = str(ROOT / "tools" / "qualification_archive.py")
    session.run("python", "-I", helper, "sdist", str(raw), str(sdist), epoch)
    session.run(
        *builder, "--no-isolation", "--wheel", "--outdir", str(output / "direct"),
        env=environment,
    )
    extracted = staging / "archive"
    extracted.mkdir()
    session.run("python", "-m", "tarfile", "-e", str(sdist), str(extracted))
    (source,) = extracted.iterdir()
    session.run(
        *builder, "--no-isolation", "--wheel", "--outdir",
        str(output / "source"), str(source), env=environment,
    )
    (direct,) = (output / "direct").glob("*.whl")
    (rebuilt,) = (output / "source").glob("*.whl")
    session.run("python", "-I", helper, "wheel", str(ROOT), str(direct), str(rebuilt))


def _installed(session):
    (wheel,) = (_artifacts() / "source").glob("*.whl")
    helper = str(ROOT / "tools" / "qualification_archive.py")
    session.run("python", "-I", helper, "install", str(wheel))
    temporary = Path(session.create_tmp()).resolve()
    session.chdir(str(temporary))
    session.run(
        "python", "-I", "-c",
        "from pathlib import Path; import precis_i18n, sysconfig; "
        "assert Path(sysconfig.get_path('purelib')) in Path(precis_i18n.__file__).parents; "
        "assert precis_i18n.get_profile('UsernameCaseMapped').enforce('Example') == 'example'",
    )
    return temporary


@nox.session(python=PYTHONS, reuse_venv=False)
def installed(session):
    """Run the same suite from copied tests against an isolated installed wheel."""
    temporary = _installed(session)
    _install_tools(session)
    shutil.copytree(ROOT / "test", temporary / "test", ignore=shutil.ignore_patterns("__pycache__"))
    session.run(
        "python", "-I", "-m", "pytest", "-ra",
        *_report(session, "wheel"), *(session.posargs or ["test"]),
        env={"PYTEST_ADDOPTS": "", "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
    )


@nox.session(python=PYTHONS, reuse_venv=False)
def runtime(session):
    """Exercise an isolated wheel with only its declared runtime dependencies."""
    _installed(session)
    session.run(
        "python", "-I", "-c",
        "from importlib.util import find_spec; assert find_spec('unicodedata2') is None; "
        "assert find_spec('pytest') is None",
    )


@nox.session(python="3.10")
def unicode_data(session):
    """Regenerate package tables from the supplied, hash-verified Unicode data."""
    session.run("python", str(ROOT / "tools" / "generate_unicode_data.py"), *session.posargs)


def _verify_unicode(session, temporary, source=None):
    if len(session.posargs) != 2:
        session.error("Supply the Unicode version and directory containing the pinned UCD inputs.")
    version, inputs = session.posargs
    golden = ROOT / "test" / ("derived-props-{}.txt".format(version.rsplit(".", 1)[0]))
    verifier = temporary / "verify_unicode.py"
    for name in ("verify_unicode.py", "generate_unicode_data.py", "unicode_sources.json"):
        shutil.copyfile(ROOT / "tools" / name, temporary / name)
    arguments = [version, str(Path(inputs).resolve()), str(golden)]
    if source:
        arguments.extend(("--source", str(source)))
    session.chdir(str(temporary))
    for language in ("C", "tr_TR.UTF-8"):
        session.run(
            "python", "-I", "-c",
            "import runpy, sys; sys.path.insert(0, sys.argv.pop(1)); "
            "runpy.run_path(sys.argv.pop(1), run_name='__main__')",
            str(temporary), str(verifier), *arguments, env={"LC_ALL": language},
        )


@nox.session(python=PYTHONS, reuse_venv=False)
def unicode_source(session):
    """Qualify a versioned Unicode provider and profile behavior from checkout."""
    _install_provider(session, required=True)
    _verify_unicode(session, Path(session.create_tmp()).resolve(), ROOT)


@nox.session(python=PYTHONS, reuse_venv=False)
def unicode_wheel(session):
    """Qualify a versioned Unicode provider and profile behavior from a wheel."""
    temporary = _installed(session)
    _install_provider(session, required=True)
    _verify_unicode(session, temporary)


@nox.session(python="3.10")
def standards_tools(session):
    """Exercise the maintained examples and check package syntax and type stubs."""
    session.install("flake8==7.3.0", "mypy==1.20.2")
    session.chdir(str(ROOT))
    session.run("python", "-m", "doctest", "README.md")
    session.run("flake8", "precis_i18n", "test", "tools", "--select=E9,F63,F7,F82")
    session.run("mypy", "--strict", "precis_i18n")


@nox.session(python="3.10")
def security(session):
    """Report medium and high static findings in production code."""
    session.install("bandit==1.9.4")
    session.run("bandit", "-ll", "-r", str(ROOT / "precis_i18n"))


@nox.session(python="3.10")
def equivalence(session):
    """Compare isolated source and wheel scenario identities and outcomes."""
    output = os.environ.get("PRECIS_QUALIFICATION_DIR")
    if not output:
        session.error("Supply the qualification directory containing the JUnit results.")
    directory = Path(output).resolve() / "results"
    session.run(
        "python", "-I", str(ROOT / "tools" / "compare_qualification.py"),
        str(directory), *(session.posargs or PYTHONS),
    )


@nox.session(python=PYTHONS, venv_backend="venv")
def benchmark(session):
    """Compare two source checkouts with the published benchmark workloads."""
    session.chdir(str(ROOT))
    session.run("python", "-IB", str(ROOT / "tools" / "benchmark_precis.py"), *session.posargs)
