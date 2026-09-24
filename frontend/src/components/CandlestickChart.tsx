'use client';

import { useMemo } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
} from 'recharts';
import type { Signal } from '@/types';

interface CandlestickChartProps {
  signal: Signal;
}

export default function CandlestickChart({ signal }: CandlestickChartProps) {
  const chartData = useMemo(() => {
    if (!signal.candles || signal.candles.length === 0) return [];

    return signal.candles.map((candle) => ({
      date: new Date(candle.d).toLocaleDateString(),
      open: candle.o,
      high: candle.h,
      low: candle.l,
      close: candle.c,
      // Calculate body color
      isUp: candle.c >= candle.o,
      // Body height
      bodyTop: Math.max(candle.o, candle.c),
      bodyBottom: Math.min(candle.o, candle.c),
      bodyHeight: Math.abs(candle.c - candle.o),
      // Wick
      wickTop: candle.h,
      wickBottom: candle.l,
    }));
  }, [signal.candles]);

  const CustomCandlestick = (props: any) => {
    const { x, y, width, height, payload } = props;
    const data = payload;
    
    if (!data) return null;

    const candleWidth = Math.max(width * 0.6, 2);
    const centerX = x + width / 2;
    const color = data.isUp ? '#10B981' : '#EF4444';

    return (
      <g>
        {/* Upper wick */}
        <line
          x1={centerX}
          y1={y + (height - (data.wickTop - data.wickBottom) / (data.wickTop - data.wickBottom) * height)}
          x2={centerX}
          y2={y + (height - (data.bodyTop - data.wickBottom) / (data.wickTop - data.wickBottom) * height)}
          stroke={color}
          strokeWidth={1}
        />
        {/* Body */}
        <rect
          x={centerX - candleWidth / 2}
          y={y + (height - (data.bodyTop - data.wickBottom) / (data.wickTop - data.wickBottom) * height)}
          width={candleWidth}
          height={Math.max((data.bodyHeight / (data.wickTop - data.wickBottom)) * height, 1)}
          fill={color}
          stroke={color}
        />
        {/* Lower wick */}
        <line
          x1={centerX}
          y1={y + (height - (data.bodyBottom - data.wickBottom) / (data.wickTop - data.wickBottom) * height)}
          x2={centerX}
          y2={y + (height - (data.wickBottom - data.wickBottom) / (data.wickTop - data.wickBottom) * height)}
          stroke={color}
          strokeWidth={1}
        />
      </g>
    );
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload[0]) return null;

    const data = payload[0].payload;
    
    return (
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-xl">
        <p className="text-white font-medium mb-2">{data.date}</p>
        <div className="space-y-1 text-sm">
          <p className="text-slate-300">Open: <span className="text-white font-mono">{data.open.toFixed(2)}</span></p>
          <p className="text-slate-300">High: <span className="text-white font-mono">{data.high.toFixed(2)}</span></p>
          <p className="text-slate-300">Low: <span className="text-white font-mono">{data.low.toFixed(2)}</span></p>
          <p className="text-slate-300">Close: <span className="text-white font-mono">{data.close.toFixed(2)}</span></p>
        </div>
      </div>
    );
  };

  if (chartData.length === 0) {
    return (
      <div className="h-80 flex items-center justify-center bg-slate-800/50 rounded-lg border border-slate-700">
        <p className="text-slate-400">No chart data available</p>
      </div>
    );
  }

  const minPrice = Math.min(...chartData.map(d => d.low));
  const maxPrice = Math.max(...chartData.map(d => d.high));
  const priceRange = maxPrice - minPrice;
  const padding = priceRange * 0.1;

  return (
    <div className="h-80 bg-slate-800/50 rounded-lg border border-slate-700 p-4">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis 
            dataKey="date" 
            stroke="#94a3b8"
            fontSize={12}
            tick={{ fill: '#94a3b8' }}
          />
          <YAxis 
            domain={[minPrice - padding, maxPrice + padding]}
            stroke="#94a3b8"
            fontSize={12}
            tick={{ fill: '#94a3b8' }}
            tickFormatter={(value) => value.toFixed(2)}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          {/* Moving average line */}
          <Line
            type="monotone"
            dataKey="close"
            stroke="#3B82F6"
            strokeWidth={2}
            dot={false}
            name="Price"
          />
          
          {/* Current price reference line */}
          {signal.live && (
            <ReferenceLine
              y={signal.live.price}
              stroke="#FBBF24"
              strokeWidth={2}
              strokeDasharray="5 5"
              label={{
                value: `Live: ${signal.live.price.toFixed(2)}`,
                position: 'right',
                fill: '#FBBF24',
                fontSize: 12,
              }}
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
