import { CardDefault } from "./Card"; // Adjust the import path as needed
import sentiment from '../../assets/sentiment.jpg';
import market from '../../assets/market.jpg';
import ai from '../../assets/ai.jpg';

export function CardContainer() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-12 bg-gray-100">
      <div className="flex flex-wrap justify-space evenly gap-5">
        <CardDefault
          imageSrc={sentiment}
          title="Sentiment Analysis"
          description="Sentiment analysis examines customer reviews to gauge overall satisfaction. Our Website helps Cafe owners understand customer preferences, improve services and dining experience, and make informed decisions, leading to better customer experiences and increased business growth."
        />
        <CardDefault
          imageSrc={market}
          title="Market Basket Analysis"
          description="Market basket analysis examines customer buying patterns to identify combinations of products frequently purchased together. For Cafe, this helps understand customer preferences, optimize menu offerings, create effective combos, and increase sales by promoting popular item pairings."
        />
        <CardDefault
          imageSrc={ai}
          title="AI Recommendations"
          description="AI uses sentiment analysis to find popular dishes and market basket analysis to identify frequently bought item combinations. This helps café owners create a menu that features customer favorites, popular combos, and optimized offerings to boost satisfaction and sales."
        />
      </div>
    </div>
  );
}
