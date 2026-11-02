import json
import unittest

from team_roadmap import groups, plan, render

with open("examples/team_results.json", encoding="utf-8") as fh:
    PEOPLE = json.load(fh)


class RoadmapTest(unittest.TestCase):
    def test_small_group_never_shown(self):
        safe, hidden = groups(PEOPLE)
        self.assertNotIn("Analytics", safe)
        self.assertEqual(hidden, 3)
        self.assertNotIn("Analytics", render(PEOPLE))

    def test_privacy_first_when_flag_common(self):
        _, _, flags, ordered = plan(PEOPLE)
        self.assertEqual(flags["data_handling_risk"], 3)
        self.assertEqual(ordered[0], "privacy")

    def test_three_windows(self):
        self.assertEqual(render(PEOPLE).count("**Days"), 3)


if __name__ == "__main__":
    unittest.main()
