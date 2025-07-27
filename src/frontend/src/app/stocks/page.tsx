"use client";

import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

type Stock = {
  ticker: string;
  description: {
    name: string;
  };
  current_price: string;
  price_change: {
    amount_change: number;
    percent_change: number;
  };
  basic_info: {
    'Market Cap': string;
  };
};

async function getStocks(): Promise<Stock[]> {
  const res = await fetch("http://localhost:8000/api/stocks");
  if (!res.ok) {
    throw new Error("Network response was not ok");
  }
  return res.json();
}

export default function StocksPage() {
  const { data: stocks, error, isLoading } = useQuery<Stock[]>({
    queryKey: ["stocks"],
    queryFn: getStocks,
  });

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-2xl font-bold mb-4">Stocks</h1>
      <Table>
        <TableCaption>A list of your stocks.</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Ticker</TableHead>
            <TableHead>Price</TableHead>
            <TableHead>Change</TableHead>
            <TableHead>Market Cap</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {stocks?.map((stock) => (
            <TableRow key={stock.ticker}>
              <TableCell>{stock.description.name}</TableCell>
              <TableCell>{stock.ticker}</TableCell>
              <TableCell>{stock.current_price}</TableCell>
              <TableCell>
                {stock.price_change.amount_change.toFixed(2)} (
                {stock.price_change.percent_change.toFixed(2)}%)
              </TableCell>
              <TableCell>{stock.basic_info['Market Cap']}</TableCell>
              <TableCell>
                <Link href={`/stocks/${stock.ticker}`}>
                  <Button variant="outline">View Details</Button>
                </Link>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
} 