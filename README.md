# Public Voices
A public conversation app enabling users to analyze comments of peers and understand different views.

URL: http://144.126.246.226:8000

*** Work in progress ***

## Problem
Social media platforms are the medium for public conversation. They enable us to speak up and express our ideas on important topics. However due to the huge number of posts, listening to this conversation is not always easy. We can easily lose the overview, get informed by fake news or always read one-sided arguments because of personalization.

## Solution
On this platform, users can create topics, comment on other's topics and see the automated comment reports. Comment reports include information about:
1. How many people agree or disagree with the initial comment?
3. What are the most common word groups used in the comments?
4. What are the word groups affecting user likelihood to agree?
5. What is the user sentiment on the topic?
6. What is the spam rate? Which were the comments flagged as spam and excluded?

This information helps users to understand the public opinion on a topic and to get a better overview of the conversation.

## Getting started
1. Clone the repository
2. Create a MongoDB database and collections <code>users</code>, <code>topics</code>, <code> comments </code>.
2. Create the <code> .env </code> file entering the your MongoDB URI. An example can be found in <code> example.env</code>.
3. Run <code> docker compose up </code> 
4. Visit <code> localhost:8000 </code> to view the app.

