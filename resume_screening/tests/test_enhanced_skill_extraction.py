import unittest
from ..utils.enhanced_skill_extraction import EnhancedSkillExtractor

class TestEnhancedSkillExtraction(unittest.TestCase):
    def setUp(self):
        self.extractor = EnhancedSkillExtractor()
    
    def test_basic_skill_extraction(self):
        text = "Strong Python programming skills required. Experience with React and Node.js preferred."
        skills = self.extractor.extract_skills_with_confidence(text)
        
        # Check if Python was found with high confidence
        python_skill = next((s for s in skills if s['name'] == 'Python'), None)
        self.assertIsNotNone(python_skill, "Python skill should be found")
        if python_skill:  # Only access dictionary if skill was found
            self.assertGreater(python_skill['confidence'], 0.8)  # High confidence due to "strong" and "required"
            self.assertEqual(python_skill['skill_level'], 'expert')  # Should detect "strong" as expert level
        
        # Check if React was found with medium confidence
        react_skill = next((s for s in skills if s['name'] == 'React'), None)
        self.assertIsNotNone(react_skill, "React skill should be found")
        if react_skill:  # Only access dictionary if skill was found
            self.assertLess(react_skill['confidence'], 0.8)  # Lower confidence due to "preferred"
    
    def test_acronym_detection(self):
        text = "Experience with AWS and ML required. Knowledge of NLP is a plus."
        skills = self.extractor.extract_skills_with_confidence(text)
        
        # Check if AWS was found
        aws_skill = next((s for s in skills if s['name'] == 'AWS'), None)
        self.assertIsNotNone(aws_skill, "AWS skill should be found")
        
        # Check if Machine Learning was found
        ml_skill = next((s for s in skills if s['name'] == 'Machine Learning'), None)
        self.assertIsNotNone(ml_skill, "Machine Learning skill should be found")
        
        # Check if NLP was found
        nlp_skill = next((s for s in skills if s['name'] == 'Natural Language Processing (NLP)'), None)
        self.assertIsNotNone(nlp_skill, "NLP skill should be found")
    
    def test_negation_handling(self):
        text = "Python required. Experience with React not required. No need for Angular."
        skills = self.extractor.extract_skills_with_confidence(text)
        
        # Python should be found
        python_skill = next((s for s in skills if s['name'] == 'Python'), None)
        self.assertIsNotNone(python_skill, "Python skill should be found")
        
        # React and Angular should not be in results due to negation
        react_skill = next((s for s in skills if s['name'] == 'React'), None)
        angular_skill = next((s for s in skills if s['name'] == 'Angular'), None)
        self.assertIsNone(react_skill, "React skill should not be found due to negation")
        self.assertIsNone(angular_skill, "Angular skill should not be found due to negation")
    
    def test_fuzzy_matching(self):
        text = "Experience in Pythno and Reactjs required."  # Intentional typos
        skills = self.extractor.extract_skills_with_confidence(text)
        
        # Should find Python despite typo
        python_skill = next((s for s in skills if s['name'] == 'Python'), None)
        self.assertIsNotNone(python_skill, "Python skill should be found despite typo")
        if python_skill:  # Only access dictionary if skill was found
            self.assertLess(python_skill['confidence'], 1.0)  # Lower confidence due to typo
        
        # Should find React despite different format
        react_skill = next((s for s in skills if s['name'] == 'React'), None)
        self.assertIsNotNone(react_skill, "React skill should be found")
    
    def test_context_importance(self):
        text1 = "Python is required for this position."
        text2 = "Python would be nice to have."
        
        skills1 = self.extractor.extract_skills_with_confidence(text1)
        skills2 = self.extractor.extract_skills_with_confidence(text2)
        
        python1 = next((s for s in skills1 if s['name'] == 'Python'), None)
        python2 = next((s for s in skills2 if s['name'] == 'Python'), None)
        
        self.assertIsNotNone(python1, "Python skill should be found in text1")
        self.assertIsNotNone(python2, "Python skill should be found in text2")
        if python1 and python2:  # Only access dictionary if both skills were found
            self.assertGreater(python1['context_importance'], python2['context_importance'])
    
    def test_skill_level_detection(self):
        text = """
        - Expert level Python programming
        - Intermediate knowledge of React
        - Basic understanding of Angular
        """
        skills = self.extractor.extract_skills_with_confidence(text)
        
        python_skill = next((s for s in skills if s['name'] == 'Python'), None)
        react_skill = next((s for s in skills if s['name'] == 'React'), None)
        angular_skill = next((s for s in skills if s['name'] == 'Angular'), None)
        
        self.assertIsNotNone(python_skill, "Python skill should be found")
        self.assertIsNotNone(react_skill, "React skill should be found")
        self.assertIsNotNone(angular_skill, "Angular skill should be found")
        
        if python_skill and react_skill and angular_skill:  # Only access dictionary if all skills were found
            self.assertEqual(python_skill['skill_level'], 'expert')
            self.assertEqual(react_skill['skill_level'], 'intermediate')
            self.assertEqual(angular_skill['skill_level'], 'beginner')

if __name__ == '__main__':
    unittest.main() 