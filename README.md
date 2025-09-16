# Flask OCR App

このアプリケーションは画像からテキストを抽出するOCR（光学文字認識）機能を提供します。

## Herokuデプロイ手順

1. Heroku CLIをインストール
2. Herokuにログイン: `heroku login`
3. アプリを作成: `heroku create your-app-name`
4. buildpackを設定:
   ```
   heroku buildpacks:set https://github.com/heroku/heroku-buildpack-apt
   heroku buildpacks:add heroku/python
   ```
5. デプロイ: `git push heroku main`

## 必要な環境変数

特に設定は不要です。Tesseractは自動的にインストールされます。

## ローカル実行

```bash
pip install -r requirements.txt
python app.py
```

## 注意事項

- HerokuではTesseractの日本語言語パックが自動的にインストールされます
- ローカル環境ではTesseractを別途インストールする必要があります
