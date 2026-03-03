# RedditStoriesPublic
Personal read-only Reddit post aggregator — fetches top/new posts from selected subreddits via the Reddit API for private use.
Reddit Post Aggregator
A lightweight, personal tool for fetching and reading posts from selected subreddits via the Reddit API. Built for private use only — no data is redistributed, sold, or shared.
Purpose
This tool creates a focused, distraction-free way to consume Reddit content from a curated list of subreddits. Instead of browsing Reddit directly, posts are fetched and displayed in a clean local interface.
What It Does

Fetches posts from a predefined list of subreddits using Reddit's official API
Calls read-only endpoints: /r/{subreddit}/hot, /r/{subreddit}/new, /r/{subreddit}/top
Makes approximately 30–50 API requests per day — well within Reddit's rate limits
Displays post titles, scores, links, and metadata locally

What It Does NOT Do

Does not post, comment, vote, or interact with Reddit in any way
Does not collect, store, or redistribute any user data
Does not run as a bot or automated account
Does not scrape at scale or bypass Reddit's API

API Usage
DetailValueAuth methodOAuth 2.0Request volume~30–50 requests/dayAccess typeRead-onlyData storageNoneRedistributionNone
Tech Stack

Python 3
PRAW (Python Reddit API Wrapper)
OAuth 2.0 via Reddit's official API

Setup

Clone the repo
Install dependencies: pip install praw
Add your Reddit API credentials to a .env file:

CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
USER_AGENT=reddit-reader/1.0 by u/yourusername

Run the script: python main.py

Compliance
This project complies with Reddit's Developer Terms and Data API Terms.
License
MIT — for personal use only.
