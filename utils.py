def extract_replies(comment):
    """
    Recursive function to extract nested comments and their data.
    """
    comment_data = {
        "text": comment.body,
        "upvotes": comment.score,
        "downvotes": comment.downs,
        "user_id": str(comment.author)  # Convert Redditor object to string for user_id
    }

    # If the comment has replies, extract them recursively
    if hasattr(comment, "replies"):
        comment_data["replies"] = [extract_replies(reply) for reply in comment.replies if not isinstance(reply, praw.models.MoreComments)]

    return comment_data