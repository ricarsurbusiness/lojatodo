import api from './api';

export interface Inventory {
  product_id: number;
  quantity: number;
  reserved_quantity: number;
  available_quantity: number;
}

export const inventoryService = {
  async getInventory(productId: string): Promise<Inventory | null> {
    try {
      const response = await api.get<Inventory>(`/api/v1/inventory/${productId}`);
      return response.data;
    } catch {
      // Product might not have inventory - return null silently
      return null;
    }
  },

  async getInventoryForProducts(productIds: number[]): Promise<Map<number, Inventory>> {
    const inventoryMap = new Map<number, Inventory>();
    
    // Fetch inventory for each product - ignore errors silently
    const results = await Promise.allSettled(
      productIds.map(async (id) => {
        const response = await api.get<Inventory>(`/api/v1/inventory/${id}`);
        return { id, inventory: response.data };
      })
    );
    
    // Only add successful results to the map
    results.forEach((result) => {
      if (result.status === 'fulfilled') {
        inventoryMap.set(result.value.id, result.value.inventory);
      }
    });
    
    return inventoryMap;
  },
};

export default inventoryService;