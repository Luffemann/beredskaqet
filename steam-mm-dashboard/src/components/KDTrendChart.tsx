import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import type { PlayerStats } from '../services/airtable';

interface KDTrendChartProps {
  data: PlayerStats[];
}

export const KDTrendChart = ({ data }: KDTrendChartProps) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data || data.length === 0 || !svgRef.current) return;

    // Calculate K/D per match
    const chartData = data
      .map((match, idx) => ({
        match: idx + 1,
        kd: match.Kills / (match.Death + 1),
        kills: match.Kills,
      }))
      .reverse(); // Chronological order

    const margin = { top: 20, right: 30, bottom: 30, left: 60 };
    const width = 600 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    // Scales
    const xScale = d3
      .scaleLinear()
      .domain([0, chartData.length])
      .range([0, width]);

    const yScale = d3
      .scaleLinear()
      .domain([0, Math.max(...chartData.map((d) => d.kd)) * 1.1])
      .range([height, 0]);

    // Line generator
    const line = d3
      .line<typeof chartData[0]>()
      .x((_d, i) => xScale(i))
      .y((d) => yScale(d.kd));

    // Clear previous
    d3.select(svgRef.current).selectAll('*').remove();

    // SVG setup
    const svg = d3
      .select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Grid lines
    svg
      .append('g')
      .attr('class', 'grid')
      .call(
        d3
          .axisLeft(yScale)
          .tickSize(-width)
          .tickFormat(() => '')
      )
      .style('stroke', '#0f3460')
      .style('stroke-opacity', 0.3);

    // Path
    svg
      .append('path')
      .datum(chartData)
      .attr('fill', 'none')
      .attr('stroke', '#00d4ff')
      .attr('stroke-width', 2.5)
      .attr('d', line);

    // Dots
    svg
      .selectAll('.dot')
      .data(chartData)
      .enter()
      .append('circle')
      .attr('cx', (_d, i) => xScale(i))
      .attr('cy', (d) => yScale(d.kd))
      .attr('r', 4)
      .attr('fill', '#00d4ff')
      .attr('opacity', 0.7);

    // Axes
    svg.append('g').attr('transform', `translate(0,${height})`).call(d3.axisBottom(xScale)).style('color', '#999');

    svg.append('g').call(d3.axisLeft(yScale)).style('color', '#999');

    // Labels
    svg
      .append('text')
      .attr('x', width / 2)
      .attr('y', height + 30)
      .attr('text-anchor', 'middle')
      .attr('fill', '#999')
      .text('Match #');

    svg
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', -50)
      .attr('text-anchor', 'middle')
      .attr('fill', '#999')
      .text('K/D Ratio');
  }, [data]);

  return (
    <div className="bg-card border border-blue-900 rounded-lg p-4">
      <h3 className="text-primary font-bold mb-4">K/D Trend</h3>
      <svg ref={svgRef}></svg>
    </div>
  );
};
