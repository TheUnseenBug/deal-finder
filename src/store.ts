import { create, useStore } from "zustand";
import { PersistOptions, persist } from "zustand/middleware";
import { Product, Store } from "./types/product";

const customStorage: PersistOptions<Store, Store>["storage"] = {
  getItem: async (name) => {
    const item = localStorage.getItem(name);
    return item ? JSON.parse(item) : null;
  },
  setItem: async (name, value) => {
    localStorage.setItem(name, JSON.stringify(value));
  },
  removeItem: async (name) => {
    localStorage.removeItem(name);
  },
};

const useTodoStore = create<Store>()(
  persist(
    (set, get) => ({
      products: [],

      addSales: (product: Product) =>
        set((state) => ({
          products: [
            ...state.products,
            {
              title: product.title,
              description: product.description,
              image: product.image,
              price: product.price,
              pricePrefix: product.pricePrefix,
            },
          ],
        })),
    }),
    {
      name: "todo-storage", // Localstorage nyckel
      storage: customStorage, // Använda custom storage
    }
  )
);

export default useStore;
