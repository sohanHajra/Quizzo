import json
import unittest

from tasks.Quiz_Generator.question_validation import is_distinct, parse_question


class QuizQuestionTests(unittest.TestCase):
    def setUp(self):
        self.good = {
            "question": "What does the document say about this topic?",
            "choices": [{"key": k, "value": v} for k, v in zip("ABCD", ["First", "Second", "Third", "Fourth"])],
            "answer": "B",
            "explanation": "The second choice is supported by the document.",
        }

    def test_valid_json_and_code_fence(self):
        self.assertEqual(parse_question(json.dumps(self.good))["answer"], "B")
        self.assertEqual(parse_question("```json\n" + json.dumps(self.good) + "\n```"), self.good)

    def test_reject_invalid_answer_schema(self):
        bad = dict(self.good, answer="E")
        with self.assertRaises(ValueError):
            parse_question(json.dumps(bad))
        with self.assertRaises(ValueError):
            parse_question("not JSON")

    def test_reject_missing_choice(self):
        bad = dict(self.good, choices=self.good["choices"][:3])
        with self.assertRaises(ValueError):
            parse_question(json.dumps(bad))

    def test_duplicate_detection(self):
        previous = ["What does the passage say about the key event in history?"]
        self.assertFalse(is_distinct(previous[0], previous))
        self.assertFalse(is_distinct("What does the passage say about the key event in geography?", previous))
        self.assertTrue(is_distinct("How is the human circulatory system organized?", previous))


if __name__ == "__main__":
    unittest.main()
