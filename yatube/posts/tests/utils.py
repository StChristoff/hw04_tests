

def post_response(response, test_post):
    post = response.context['page_obj'][0]
    cont_test = {
        post.text: test_post.text,
        post.group: test_post.group,
        post.author: test_post.author,
    }
    return cont_test

    # Для test_views.py
    # for post, test_post in post_response(
    #     response, PostsViewsTests.test_post
    #     ).items():
    #     with self.subTest(post=post):
    #         self.assertEqual(post, test_post)
