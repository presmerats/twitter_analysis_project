import unittest
from scraping import search_for_replies
from scraping import write_row 
from scraping import 

class TestGraph(unittest.TestCase):

    def setUp(self):
        
        self.setup_var = True

    def test_recursion_in_loop_form(self):
        """
            mock   limit_handled(
                tweepy.Cursor(
                    api.search, 
                    q=query, 
                    tweet_mode='extended'
                    ).items(limit))

            mock write_row()

            so you just control the ouptut of search_for_replies

        """
        self.assertTrue(self.setup_var)

    def test_depth(self):
        """ tests that graph generation uses correctly the depth parameter
        """
        self.assertTrue(False)

    def test_breadth(self):
        """ tests that graph generation uses correctly the breadth parameter
        """
        self.assertTrue(False)


    def test_unique_entries(self):
        """ 
        """
        self.assertTrue(False)





    def test_rate_limiting(self):
        """ 
        """
        self.assertTrue(True)


    def test_extracted_graph(self):
        """ 
            use mock intensively here
        """
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()