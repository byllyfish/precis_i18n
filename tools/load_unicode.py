# load_unicode.py

# Load unicode data into a sqlite database.
#
#  cp   codepoint
#  name name
#  cat  general_category
#  combining  combining_category
#  bidi

import re
import sqlite3


class UnicodeDatabase(object):
    property_regex = re.compile(r"^([0-9A-F]+)(?:\.\.([0-9A-F]+))?\s*;\s*(\S+)\s*[#;]")

    def __init__(self, filename):
        self._conn = sqlite3.connect(filename)

    def load(self):
        """Load database files."""
        self.create_tables()
        self.parse_unicodedata("UnicodeData.txt")
        self.add_non_characters()
        self.parse_properties("DerivedAge.txt", "age")
        self.parse_properties("Scripts.txt", "script")
        self.parse_properties("HangulSyllableType.txt", "hst")

        self.add_reserved_dicp()
        self.parse_property_present(
            "DerivedCoreProperties.txt", "dicp", "Default_Ignorable_Code_Point"
        )
        self.parse_property_present(
            "DerivedNormalizationProps.txt", "fce", "Full_Composition_Exclusion"
        )
        self.add_exceptions()
        self.assign_has_compat()
        self.assign_precis()
        self._conn.commit()

    def create_tables(self):
        """Create database tables."""
        cur = self._conn.cursor()
        ddl = """
            CREATE TABLE codepoints (
              cp         INTEGER PRIMARY KEY,
              name       TEXT NOT NULL,
              category   TEXT NOT NULL,
              combining  INTEGER NOT NULL,
              bidi       TEXT NOT NULL,
              decomp     TEXT NOT NULL,
              first_cp   INTEGER NOT NULL,  -- first cp in canonical decomp, -1 means no decomp, -2 means
              age        REAL,
              script     TEXT,
              hst        TEXT,       -- HangulSyllableType
              dicp       INT,        -- Default_Ignorable_Code_Point
              fce        INT,        -- Full_Composition_Exclusion
              has_compat INT,
              precis     TEXT
            )
        """
        cur.execute(ddl)

    def parse_unicodedata(self, filename):
        """Load data from UnicodeData.txt file."""
        cur = self._conn.cursor()
        for line in open(filename):
            cols = line.split(";")
            cp = int(cols[0], 16)
            name = cols[1]
            if name.endswith(", First>"):
                first = cp
            elif name.endswith(", Last>"):
                name = name[:-7] + " %4.4x-%4.4x>" % (first, cp)
                for n in range(first, cp + 1):
                    self._insert(cur, n, name, cols[2], cols[3], cols[4], cols[5])
            else:
                self._insert(cur, cp, name, cols[2], cols[3], cols[4], cols[5])

    def add_non_characters(self):
        """Add entries for non-characters."""
        cur = self._conn.cursor()
        for cp in range(0xFDD0, 0xFDEF + 1):
            self._insert(cur, cp, "<noncharacter>", "Cn", 0, "", "")
        for n in range(0, 17):
            cp1 = (n << 16) | 0xFFFE
            cp2 = (n << 16) | 0xFFFF
            self._insert(cur, cp1, "<noncharacter>", "Cn", 0, "", "")
            self._insert(cur, cp2, "<noncharacter>", "Cn", 0, "", "")

    def add_reserved_dicp(self):
        """Add entries for <reserved> chars that have the 'dicp' property."""
        cur = self._conn.cursor()
        self._insert(cur, 0x2065, "<reserved>", "Cn", 0, "", "")
        for cp in range(0xFFF0, 0xFFF8 + 1):
            self._insert(cur, cp, "<reserved>", "Cn", 0, "", "")
        self._insert(cur, 0xE0000, "<reserved>", "Cn", 0, "", "")
        for cp in range(0xE0002, 0xE001F + 1):
            self._insert(cur, cp, "<reserved>", "Cn", 0, "", "")
        for cp in range(0xE0080, 0xE00FF + 1):
            self._insert(cur, cp, "<reserved>", "Cn", 0, "", "")
        for cp in range(0xE01F0, 0xE0FFF + 1):
            self._insert(cur, cp, "<reserved>", "Cn", 0, "", "")

    def parse_properties(self, filename, column):
        """Load data from a Unicode property file."""
        cur = self._conn.cursor()
        for line in open(filename):
            line = line[:-1]
            if not line or line[0] == "#":
                continue
            m = self.property_regex.match(line)
            if not m:
                raise ValueError("Parse failed: %s" % line)
            self._set_column(cur, column, m.group(1), m.group(2), m.group(3))

    def parse_property_present(self, filename, column, value):
        """Load data from a Unicode property file. Set `column` to 1 if we
        find `value`.
        """
        cur = self._conn.cursor()
        for line in open(filename):
            line = line[:-1]
            if not line or line[0] == "#":
                continue
            m = self.property_regex.match(line)
            if not m:
                raise ValueError("Parse failed: %s" % line)
            if m.group(3) == value:
                self._set_column(cur, column, m.group(1), m.group(2), 1)

    def _insert(self, cur, cp, name, category, combining, bidi, decomp):
        """Insert a codepoint into table."""
        # Set `first_cp` depending on the value of the `decomp` field. If
        # `decomp` is empty, set first_cp to -1. If `decomp` is a compatibility
        # decomposition (starts with '<'), set first_cp to -2. Otherwise, set
        # first_cp to the character code of the first codepoint in `decomp`.
        if not decomp:
            first_cp = -1
        elif decomp.startswith("<"):
            first_cp = -2
        else:
            first_cp = int(decomp.split()[0], 16)
        cur.execute(
            "INSERT INTO codepoints (cp, name, category, combining, bidi, decomp, first_cp) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (cp, name, category, int(combining), bidi, decomp, first_cp),
        )

    def _set_column(self, cur, column, first, last, value):
        """Set a specific column in the"""
        first = int(first, 16)
        last = int(last, 16) if last else first
        sql = "UPDATE codepoints SET %s=? WHERE cp=? AND %s IS NULL" % (column, column)
        for cp in range(first, last + 1):
            cur.execute(sql, (value, cp))
            if cur.rowcount != 1:
                print(
                    "failed update: %4.4x  %s=%s [%04x-%04x]"
                    % (cp, column, value, first, last)
                )

    def add_exceptions(self):
        """Add PRECIS exceptions."""
        sql = """
        UPDATE codepoints SET precis = 'PVALID/exceptions' WHERE cp in (0x00DF,
            0x03C2, 0x06FD, 0x06FE, 0x0F0B, 0x3007);
        UPDATE codepoints SET precis = 'CONTEXTO/exceptions' WHERE cp in (0x00B7, 0x0375,
            0x05F3, 0x05F4, 0x30FB, 0x0660, 0x0661, 0x0662, 0x0663, 0x0664,
            0x0665, 0x0666, 0x0667, 0x0668, 0x0669, 0x06F0, 0x06F1, 0x06F2,
            0x06F3, 0x06F4, 0x06F5, 0x06F6, 0x06F7, 0x06F8, 0x06F9);
        UPDATE codepoints SET precis = 'DISALLOWED/exceptions' WHERE cp in (
            0x0640, 0x07FA, 0x302E, 0x302F, 0x3031, 0x3032, 0x3033, 0x3034,
            0x3035, 0x303B);
        """
        cur = self._conn.cursor()
        cur.executescript(sql)

    def assign_precis(self):
        """Assign precis derived property value to each codepoint.

        This is called after exceptions and backward_compatible have been
        assigned their precis properties.
        """
        sql = """
            UPDATE codepoints SET precis = (
              CASE
              -- unassigned
              WHEN category = 'Cn' AND name != '<noncharacter>' THEN 'UNASSIGNED/unassigned'
              -- ascii7
              WHEN cp BETWEEN 0x21 AND 0x7E THEN 'PVALID/ascii7'
              -- join_control
              WHEN cp BETWEEN 0x200c AND 0x200d THEN 'CONTEXTJ/join_control'
              -- old_hangul_jamo
              WHEN hst IN ('L', 'V', 'T') THEN 'DISALLOWED/old_hangul_jamo'
              -- precis_ignorable_properties
              WHEN dicp == 1 OR name == '<noncharacter>' THEN 'DISALLOWED/precis_ignorable_properties'
              -- controls
              WHEN category = 'Cc' THEN 'DISALLOWED/controls'
              -- has_compat
              WHEN has_compat = 1 THEN 'FREE_PVAL/has_compat'
              -- letter_digits
              WHEN category IN ('Ll', 'Lu', 'Lo', 'Nd', 'Lm', 'Mn', 'Mc') THEN 'PVALID/letter_digits'
              -- other_letter_digits
              WHEN category IN ('Lt', 'Nl', 'No', 'Me') THEN 'FREE_PVAL/other_letter_digits'
              -- spaces
              WHEN category = 'Zs' THEN 'FREE_PVAL/spaces'
              -- symbols
              WHEN category IN ('Sm', 'Sc', 'Sk', 'So') THEN 'FREE_PVAL/symbols'
              -- punctuation
              WHEN category IN ('Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po') THEN 'FREE_PVAL/punctuation'
              -- other
              ELSE 'DISALLOWED/other'
              END
            ) WHERE precis IS NULL
        """
        cur = self._conn.cursor()
        cur.execute(sql)

    def assign_has_compat(self):
        """Assign true to characters that have compatibility decompositions.
        For these, `normalize('NFKC', ch) != ch`.
        """
        cur = self._conn.cursor()
        # Set has_compat=1 for characters whose decomp field begins with '<' or
        # has a 'full composition exclusion' of 1.
        sql = """
            UPDATE codepoints SET has_compat=1 WHERE decomp LIKE '<%' OR fce = 1
        """
        cur.execute(sql)
        # The set of codepoints with compatibility decompositions is not complete
        # until we include the set of approximately 15 chars whose CANONICAL
        # decomposition has a further COMPATIBILITY decomposition.
        sql = """
            UPDATE codepoints SET has_compat=1 WHERE cp IN (
                SELECT a.cp from codepoints a, codepoints b  WHERE b.cp = a.first_cp AND b.first_cp == -2
            )
        """
        cur.execute(sql)

    def check_has_compat(self, ucd):
        """Check that has_compat is set to 1 for every character where
        normalize(NFKC, ch) != ch.
        """
        cur = self._conn.cursor()
        sql = "SELECT cp, has_compat, age FROM codepoints WHERE age <= %g" % ucd.version
        for cp, has_compat, age in cur.execute(sql):
            char = chr(cp)
            norm = ucd.normalize("NFKC", char)
            if has_compat == 1:
                if norm == char:
                    print("Invalid has_compat=1 for cp=%d, age=%s" % (cp, age))
            else:
                if norm != char:
                    print("Invalid has_compat=0 for cp=%d, age=%s" % (cp, age))

    def check_precis(self, ucd):
        """Compare derived property computation to `precis` value in database."""
        from precis_i18n.derived import derived_property

        cur = self._conn.cursor()
        sql = "SELECT cp, precis, age FROM codepoints WHERE age <= %g" % UCD.version
        for cp, precis, age in cur.execute(sql):
            prop = "%s/%s" % derived_property(cp, ucd)
            if prop != precis:
                print(
                    "Different precis value: %s vs %s for cp=%d, age=%s"
                    % (prop, precis, cp, age)
                )


if __name__ == "__main__":
    try:
        db = UnicodeDatabase("unicode.db")
        db.load()
    except sqlite3.OperationalError:
        pass

    from precis_i18n.unicode import UnicodeData

    UCD = UnicodeData()
    db.check_has_compat(UCD)
    db.check_precis(UCD)
