"use client";

import { useQuery } from "@tanstack/react-query";
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";

type StockDetails = {
    description: {
        name: string;
        about: string;
    };
    basic_info: {
        [key: string]: string;
    };
    pros_and_cons: {
        pros: string[];
        cons: string[];
    };
    top_news: {
        name: string;
        link: string;
    }[];
};

async function getStockDetails(ticker: string): Promise<StockDetails> {
    const res = await fetch(`http://localhost:8000/api/stocks/${ticker}`);
    if (!res.ok) {
        throw new Error("Network response was not ok");
    }
    return res.json();
}

export default async function StockDetailsPage({
    params,
}: {
    params: Promise<{ ticker: string }>;
}) {
    const { ticker } = await params;
    const {
        data: stock,
        error,
        isLoading,
    } = useQuery<StockDetails>({
        queryKey: ["stockDetails", ticker],
        queryFn: () => getStockDetails(ticker),
        enabled: !!ticker,
    });

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error.message}</div>;
    }

    return (
        <div className="container mx-auto py-10">
            <h1 className="text-3xl font-bold mb-2">{stock?.description.name}</h1>
            <p className="text-gray-600 mb-8">{stock?.description.about}</p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <Card>
                    <CardHeader>
                        <CardTitle>Basic Info</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ul>
                            {stock?.basic_info &&
                                Object.entries(stock.basic_info).map(([key, value]) => (
                                    <li key={key}>
                                        <strong>{key}:</strong> {value}
                                    </li>
                                ))}
                        </ul>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Pros & Cons</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <h4 className="font-bold text-lg mb-2">Pros</h4>
                        <ul className="list-disc list-inside mb-4">
                            {stock?.pros_and_cons.pros.map((pro, index) => (
                                <li key={index}>{pro}</li>
                            ))}
                        </ul>
                        <h4 className="font-bold text-lg mb-2">Cons</h4>
                        <ul className="list-disc list-inside">
                            {stock?.pros_and_cons.cons.map((con, index) => (
                                <li key={index}>{con}</li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Top News</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ul>
                            {stock?.top_news.map((news, index) => (
                                <li key={index} className="mb-2">
                                    <a
                                        href={news.link}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-blue-600 hover:underline"
                                    >
                                        {news.name}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
} 