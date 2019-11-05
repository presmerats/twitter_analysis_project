
import unittest
from unittest import mock
from unittest.mock import patch, Mock
from scraping import search_for_replies

class myObject(object):
    pass

def mock_cursor2(args, **kwargs):
    ob = myObject() 
    ob.items = lambda x: None
    return ob

def mock_limit_handled_side_effect(args, **kwargs):
    ob = myObject() 
    ob.created_at = "Wed Oct 10 20:19:24 +0000 2018"
    ob.id = 123456
    ob.id_str = "123456"
    ob.text = "yay!"
    ob.full_text = "yay!"
    ob.user = myObject()
    ob.user.screen_name = "pepitoPerez"
    ob.user.followers_count = 3
    ob.lang = 'es'
    ob.favorited = False
    ob.retweeted = False
    ob.entities = []

    return [ob,]

class TestGraph(unittest.TestCase):

    def setUp(self):
        """
            What to setup here?
        """
        self.setup_var = True

        self.tweet = myObject() 
        self.tweet.created_at = "Wed Oct 10 20:19:24 +0000 2018"
        self.tweet.id = 123456
        self.tweet.id_str = "123456"
        self.tweet.text = "yay!"
        self.tweet.full_text = "yay!"
        self.tweet.user = myObject()
        self.tweet.user.screen_name = "pepitoPerez"
        self.tweet.user.followers_count = 3
        self.tweet.lang = 'es'
        self.tweet.favorited = False
        self.tweet.retweeted = False
        self.tweet.entities = []
        

    
    @mock.patch('scraping.init_results_file',return_value=None)
    @mock.patch('tweepy.Cursor', side_effect=mock_cursor2 )
    @mock.patch('scraping.limit_handled', side_effect=mock_limit_handled_side_effect)
    @mock.patch('scraping.write_row', return_value=True)
    def test_recursion_in_loop_form(self, mock_write_row, mock_limit_handled, mock_Cursor, mock_init_results_file):
        """
            mock   limit_handled()
                tweepy.Cursor()
                write_row and init_results_file()

            so you just control the ouptut of search_for_replies

        """

        # verify the mocks assignment
        # print(mock_init_results_file)
        # print(mock_Cursor)       
        # print(mock_limit_handled)
        # print(mock_write_row)

        # run the test
        user_name = 'pepito_perez'
        search_for_replies(user_name,limit=1)
        
        # assert facts (order matters! becareful if inside a loop)


        mock_init_results_file.assert_called_with('../data/graphs/pepito_perez_replies.csv', 'w', None)
        mock_limit_handled.assert_called_with(None)
        mock_write_row.assert_called_with('../data/graphs/%s.csv' % (user_name+'_replies'),'w',['Wed Oct 10 20:19:24 +0000 2018', 'pepitoPerez', 3, 'es', False, False, 'pepito_perez'])

    def _test_depth(self):
        """ tests that graph generation uses correctly the depth parameter
        """
        self.assertTrue(False)

    def _test_breadth(self):
        """ tests that graph generation uses correctly the breadth parameter
        """
        self.assertTrue(False)


    def _test_unique_entries(self):
        """ 
        """
        self.assertTrue(False)

    def _test_rate_limiting(self):
        """ 
        """
        self.assertTrue(False)


    def _test_extracted_graph(self):
        """ 
            use mock intensively here
        """
        self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()