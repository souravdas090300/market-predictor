import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Market Predictor - AI-Powered Market Analysis</title>
        <meta name="description" content="Advanced market prediction using machine learning, technical analysis, and sentiment analysis" />
        <link rel="icon" href="/market_predictor_favicon_32x32.png" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
