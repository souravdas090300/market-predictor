import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import type { Signal, RiskAnalysis, StrategyOptimization } from '@/types';

export class PDFExporter {
  private doc: jsPDF;

  constructor() {
    this.doc = new jsPDF();
  }

  addTitle(title: string): void {
    this.doc.setFontSize(20);
    this.doc.setTextColor(0, 0, 0);
    this.doc.text(title, 14, 20);
    this.doc.setFontSize(10);
    this.doc.setTextColor(100, 100, 100);
    this.doc.text(`Generated on ${new Date().toLocaleString()}`, 14, 28);
    this.doc.setLineWidth(0.5);
    this.doc.line(14, 32, 196, 32);
  }

  addSignalReport(signal: Signal): void {
    this.addTitle(`Market Signal Report - ${signal.symbol}`);
    
    // Signal overview
    this.doc.setFontSize(14);
    this.doc.setTextColor(0, 0, 0);
    this.doc.text('Signal Overview', 14, 45);
    
    const signalData = [
      ['Symbol', signal.symbol],
      ['Name', signal.name],
      ['Asset Class', signal.class],
      ['Signal', signal.signal.toUpperCase()],
      ['Probability Up', `${(signal.probability_up * 100).toFixed(1)}%`],
      ['Conviction', `${(signal.conviction * 100).toFixed(0)}%`],
      ['Model Probability', `${(signal.model_probability_up * 100).toFixed(1)}%`],
      ['Analysis Date', signal.as_of],
    ];
    
    autoTable(this.doc, {
      startY: 50,
      head: [['Metric', 'Value']],
      body: signalData,
      theme: 'grid',
      headStyles: { fillColor: [66, 139, 202] },
    });

    // Indicators
    this.doc.setFontSize(14);
    this.doc.text('Technical Indicators', 14, this.doc.lastAutoTable.finalY + 15);
    
    const indicatorData = [
      ['RSI (14)', signal.indicators.rsi_14.toFixed(2)],
      ['vs SMA50', `${signal.indicators.vs_sma_50_pct.toFixed(2)}%`],
      ['Volatility (20d)', `${signal.indicators.volatility_20d_pct.toFixed(2)}%`],
    ];
    
    autoTable(this.doc, {
      startY: this.doc.lastAutoTable.finalY + 20,
      head: [['Indicator', 'Value']],
      body: indicatorData,
      theme: 'grid',
      headStyles: { fillColor: [66, 139, 202] },
    });

    // Sentiment
    this.doc.setFontSize(14);
    this.doc.text('News Sentiment', 14, this.doc.lastAutoTable.finalY + 15);
    
    const sentimentData = [
      ['Sentiment Score', signal.sentiment.score.toFixed(2)],
      ['Headlines Count', signal.sentiment.headline_count.toString()],
    ];
    
    autoTable(this.doc, {
      startY: this.doc.lastAutoTable.finalY + 20,
      head: [['Metric', 'Value']],
      body: sentimentData,
      theme: 'grid',
      headStyles: { fillColor: [66, 139, 202] },
    });

    // Backtest results
    if (signal.backtest) {
      this.doc.setFontSize(14);
      this.doc.text('Backtest Results', 14, this.doc.lastAutoTable.finalY + 15);
      
      const backtestData = [
        ['Accuracy', `${(signal.backtest.accuracy * 100).toFixed(1)}%`],
        ['Baseline Accuracy', `${(signal.backtest.baseline_accuracy * 100).toFixed(1)}%`],
        ['Sample Size', signal.backtest.samples.toString()],
      ];
      
      autoTable(this.doc, {
        startY: this.doc.lastAutoTable.finalY + 20,
        head: [['Metric', 'Value']],
        body: backtestData,
        theme: 'grid',
        headStyles: { fillColor: [66, 139, 202] },
      });
    }

    // Candlestick patterns
    if (signal.candle_patterns && signal.candle_patterns.length > 0) {
      this.doc.addPage();
      this.doc.setFontSize(14);
      this.doc.text('Candlestick Patterns', 14, 20);
      
      const patternData = signal.candle_patterns.map(p => [
        p.pattern,
        p.bias,
        p.meaning.substring(0, 50) + (p.meaning.length > 50 ? '...' : '')
      ]);
      
      autoTable(this.doc, {
        startY: 30,
        head: [['Pattern', 'Bias', 'Meaning']],
        body: patternData,
        theme: 'grid',
        headStyles: { fillColor: [66, 139, 202] },
      });
    }
  }

  addRiskReport(risk: RiskAnalysis): void {
    this.addTitle(`Risk Analysis Report - ${risk.symbol}`);
    
    const riskData = [
      ['Symbol', risk.symbol],
      ['Entry Price', `$${risk.entry_price.toFixed(2)}`],
      ['Stop Loss', `$${risk.stop_loss.toFixed(2)}`],
      ['Take Profit', `$${risk.take_profit.toFixed(2)}`],
      ['Position Size', risk.position_size.toFixed(2)],
      ['Risk Amount', `$${risk.risk_amount.toFixed(2)}`],
      ['Risk Percentage', `${risk.risk_percent.toFixed(2)}%`],
      ['Potential Profit', `$${risk.potential_profit.toFixed(2)}`],
      ['Potential Loss', `$${risk.potential_loss.toFixed(2)}`],
      ['Risk/Reward Ratio', risk.risk_reward_ratio.toFixed(2)],
      ['Recommended Position', risk.recommended_position_size.toFixed(2)],
      ['Max Position Size', risk.max_position_size.toFixed(2)],
    ];
    
    autoTable(this.doc, {
      startY: 40,
      head: [['Metric', 'Value']],
      body: riskData,
      theme: 'grid',
      headStyles: { fillColor: [220, 53, 69] },
    });
  }

  addStrategyReport(strategy: StrategyOptimization): void {
    this.addTitle(`Strategy Optimization Report - ${strategy.symbol}`);
    
    // Best parameters
    this.doc.setFontSize(14);
    this.doc.text('Optimal Parameters', 14, 45);
    
    const paramData = [
      ['Strategy Type', strategy.strategy_type],
      ['Lookback Period', strategy.best_parameters.lookback_period.toString()],
      ['Holding Period', strategy.best_parameters.holding_period.toString()],
      ['Threshold', strategy.best_parameters.threshold.toFixed(2)],
    ];
    
    autoTable(this.doc, {
      startY: 50,
      head: [['Parameter', 'Value']],
      body: paramData,
      theme: 'grid',
      headStyles: { fillColor: [40, 167, 69] },
    });

    // Performance metrics
    this.doc.setFontSize(14);
    this.doc.text('Performance Metrics', 14, this.doc.lastAutoTable.finalY + 15);
    
    const perfData = [
      ['Total Return', `${(strategy.performance.total_return * 100).toFixed(2)}%`],
      ['Win Rate', `${(strategy.performance.win_rate * 100).toFixed(2)}%`],
      ['Max Drawdown', `${(strategy.performance.max_drawdown * 100).toFixed(2)}%`],
      ['Sharpe Ratio', strategy.performance.sharpe_ratio.toFixed(2)],
    ];
    
    autoTable(this.doc, {
      startY: this.doc.lastAutoTable.finalY + 20,
      head: [['Metric', 'Value']],
      body: perfData,
      theme: 'grid',
      headStyles: { fillColor: [40, 167, 69] },
    });

    // Backtest results
    if (strategy.backtest_results && strategy.backtest_results.length > 0) {
      this.doc.addPage();
      this.doc.setFontSize(14);
      this.doc.text('Backtest Results', 14, 20);
      
      const backtestData = strategy.backtest_results.map(r => [
        r.date,
        r.signal,
        `$${r.entry_price.toFixed(2)}`,
        `$${r.exit_price.toFixed(2)}`,
        `${(r.return * 100).toFixed(2)}%`
      ]);
      
      autoTable(this.doc, {
        startY: 30,
        head: [['Date', 'Signal', 'Entry', 'Exit', 'Return']],
        body: backtestData,
        theme: 'grid',
        headStyles: { fillColor: [40, 167, 69] },
      });
    }
  }

  save(filename: string): void {
    this.doc.save(filename);
  }
}

export const pdfExporter = new PDFExporter();
