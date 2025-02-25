export interface Product {
  description: string;
  image: string;
  price: string;
  pricePrefix: string;
  title: string;
}

export interface Store {
  products: Product[];
  addSales: (product: Product) => void;
}
