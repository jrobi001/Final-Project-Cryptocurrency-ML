# CSV-Processing-Notes

- It seems like the badly formatted tweets don't exist when imported back into a pandas data-frame, which sort of makes sense. It may still be worth putting a check or two in still though.

- An issue may come along when BST comes in however it is possible the time is UTC, not UK time... which would save quite a bit of bother. I will have to make sure to double check the data when the clocks change on the 28th March

### Sentiment analysis notes

- It may be a good idea to filter only tweets by users over a certain follower count, or could look for the most influential users and only use them in the analysis.
  - Any method of filtering out bot posts would also be good.
- I think It's a good idea to keep the 'shared' tweets separate. They are far more likely to be spam... but can still analyse them separated.
- Most classifiers used by projects online are generic ones, not trained specifically for twitter or crypto. These will be fine to use, but could look for a more specifically trained classifer.
  - Alternative is to manually label 10s of 1000s of tweets and train own classifier (too long)

### Sentiment analysis options

- Can use [TextBlob](https://textblob.readthedocs.io/en/dev/), which has inbuilt sentiment and polarity tools [article](https://medium.com/atoti/how-im-failing-my-twitter-sentiment-analysis-for-cryptocurrency-prediction-149a1730a6fd). They use it in conjunction with the [natural language toolkit](https://www.nltk.org/) to pre-process the text.

- VADER method (in NLTK)  provides polarity and intensity. Is based on generic word scorings, so won't correctly ascribe positivity or negativity to trading terms, or twitter speak~

- Twitter BERTs (Bidirectional Encoder Representations from Transformers) - pre-trained models/word maps.
  https://link.springer.com/chapter/10.1007/978-3-030-33582-3_41
  https://github.com/mohiuddin02/TweetBERT
  https://github.com/VinAIResearch/BERTweet

  https://analyticsindiamag.com/how-i-used-bidirectional-encoder-representations-from-transformers-bert-to-analyze-twitter-data/

