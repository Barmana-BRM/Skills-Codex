# Sorftime 工具路由

直接能力：`mcp__sorftime_server__product_search`。

当前声明：

```ts
declare const tools: { mcp__sorftime_server__product_search(args: {
  // Amazon marketplace site.
  amz_site?: "Unknow" | "US" | "GB" | "DE" | "FR" | "IN" | "CA" | "JP" | "ES" | "IT" | "MX" | "AE" | "AU" | "BR" | "SA";
  // Optional: filter products of the specified brand.
  brand?: string;
  // Optional: filter products by fulfillment method. Allowed values: `Both` (default, no filter), `FBM` (seller-fulfilled), `FBA` (any product using Amazon FBA, including seller-shipped and third-party like 1688), `AmzFBA` (third-party seller using Amazon FBA, e.g. 1688).
  delivery_type?: "Both" | "FBM" | "FBA" | "AmzFBA";
  // Optional: filter products with monthly sales volume less than or equal to this value.
  month_sales_volume_max?: number;
  // Optional: filter products with monthly sales volume greater than or equal to this value.
  month_sales_volume_min?: number;
  // The page index of the query result. Defaults to page 1. Each page returns 20 records.
  page?: number;
  // Optional: filter products with selling price less than or equal to this value.
  price_max?: number;
  // Optional: filter products with selling price greater than or equal to this value.
  price_min?: number;
  // Optional: filter products whose title or attributes contain the specified property.
  property_name?: string;
  // Optional: filter products with review count less than or equal to this value.
  ratings_count_max?: number;
  // Optional: filter products with review count greater than or equal to this value.
  ratings_count_min?: number;
  // Optional: filter products with star rating less than or equal to this value.
  ratings_max?: number;
  // Optional: filter products with star rating greater than or equal to this value.
  ratings_min?: number;
  // Optional: search related products by this name.
  search_name?: string;
  // Optional: filter products that are in peak season in the specified month. Defaults to Both.
  seasonal_popular_product?: "Both" | "January" | "February" | "March" | "April" | "May" | "June" | "July" | "August" | "September" | "October" | "November" | "December";
  // Optional: filter products of the specified seller.
  seller_name?: string;
  // Optional: if true, sort by the product's potential index from high to low.
  sortby_potential_index?: boolean;
  // Optional: filter products whose sales volume rank in the subcategory is less than or equal to this value.
  subcategory_sales_volume_rank_max?: number;
  // Optional: filter products whose sales volume rank in the subcategory is greater than or equal to this value.
  subcategory_sales_volume_rank_min?: number;
  // Optional: filter products whose variation (child ASIN) count is less than or equal to this value.
  variation_count_max?: number;
  // Optional: filter products whose variation (child ASIN) count is greater than or equal to this value.
  variation_count_min?: number;
}): Promise<CallToolResult>; };
```

必填与可选字段由上面声明确定。业务需要的站点或窗口仍须明确；`Unknow` 不作为有效站点替代。

## 实际执行

先复用范围匹配的授权导出或历史结果，再选择当前可用连接器。下列映射只验证了接口声明或本地代码，未验证在线鉴权、配额和真实返回。运行时重新查看工具 schema；存在同名工具也不等于字段、窗口、分页语义相同。

保留原始响应与业务状态，工具错误不得转成空数组。未提供的筛选器只可在已取得的样本上筛选，并披露样本边界。没有可用通路时交付缺口和可用数据分析，不编造接口或用其他数据源冒充指定提供方。
