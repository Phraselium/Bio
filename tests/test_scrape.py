from src.scrape import scrape

def test_scrape():
    assert scrape('http://example.com') == 'Scraped data from http://example.com'
