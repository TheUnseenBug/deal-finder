import React, { FC } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "./ui/card";
import Product from "@/types/product";

interface Props {
  data: Product;
}

const ProductCard: FC<Props> = ({ data }) => {
  return (
    <Card className="flex flex-col rounded-lg">
      <CardHeader>
        <CardTitle>{data.title}</CardTitle>
        <CardDescription>
          <p>{data.description}</p>
        </CardDescription>
      </CardHeader>
      <CardContent>
        <img src={data.image} alt="" />
      </CardContent>
      <CardFooter className="flex justify-start gap-5">
        <p>{data.pricePrefix}</p>
        <p>{data.price}</p>
      </CardFooter>
    </Card>
  );
};

export default ProductCard;
