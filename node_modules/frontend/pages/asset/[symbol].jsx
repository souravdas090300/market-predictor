import AssetDetail from '../../components/AssetDetail';
import { useRouter } from 'next/router';

export default function AssetPage() {
  const router = useRouter();
  const { symbol, category } = router.query;
  
  return symbol ? (
    <AssetDetail
      symbol={symbol}
      category={category}
      onBack={() => router.back()}
    />
  ) : null;
}
