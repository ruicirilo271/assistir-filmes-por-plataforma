from flask import Flask, render_template, request, abort
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

PLATAFORMAS = {
    "apple-tv-plus": "https://www.filmelier.com/br/streamings/apple-tv-plus",
    "netflix": "https://www.filmelier.com/br/streamings/netflix",
    "disney-plus": "https://www.filmelier.com/br/streamings/disney-plus",
    "hbo-max": "https://www.filmelier.com/br/streamings/hbo-max",
    "globoplay": "https://www.filmelier.com/br/streamings/globoplay",
    "youtube": "https://www.filmelier.com/br/streamings/youtube",
    "paramount-plus": "https://www.filmelier.com/br/streamings/paramount-plus",
    "amazon-prime-video-store": "https://www.filmelier.com/br/streamings/amazon-prime-video-store"
}

def get_filmes_filmelier(url):
    base_url = "https://www.filmelier.com"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector('a > img[data-src]')
        filmes = []

        for a in page.query_selector_all('a'):
            img = a.query_selector('img[data-src]')
            titulo_h3 = a.query_selector('h3.styles_title__3AGJt')
            href = a.get_attribute('href')
            if img and titulo_h3 and href:
                filmes.append({
                    'titulo': titulo_h3.inner_text().strip(),
                    'imagem': img.get_attribute('data-src'),
                    'slug': href.strip('/').split('/')[-1]
                })
        browser.close()
        return filmes

def obter_link_video_megafilmes(slug):
    url = f"https://megafilmeshdz.cyou/filmes/{slug}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, 'html.parser')
    for p in soup.select('.player_select_item[data-embed]'):
        embed_url = p.get('data-embed')
        if embed_url:
            return embed_url
    iframe = soup.find('iframe')
    if iframe and iframe.get('src'):
        return iframe.get('src')
    return None

@app.route("/")
def index():
    return render_template("index.html", plataformas=PLATAFORMAS)

@app.route("/plataforma/<nome>")
def plataforma(nome):
    url = PLATAFORMAS.get(nome)
    if not url:
        abort(404)
    filmes = get_filmes_filmelier(url)
    return render_template("plataforma.html", filmes=filmes, nome=nome.capitalize(), plataformas=PLATAFORMAS)

@app.route("/filme/<slug>")
def filme(slug):
    video_url = obter_link_video_megafilmes(slug)
    if not video_url:
        abort(404, description="Vídeo não encontrado")
    return render_template("filme.html", video_url=video_url, slug=slug)

if __name__ == "__main__":
    app.run(debug=True)

