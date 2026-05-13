export interface CustomerMeta {
  slug: string;
  display: string;
  sector: string;
  sector_icon: string;
  scheme_size_m: number;
  member_count: number;
  transaction_m: number;
  status: string;
}

export const CUSTOMERS: CustomerMeta[] = [
  {
    slug: "bdo",
    display: "BDO Pension Fund",
    sector: "Professional Services",
    sector_icon: "account_balance",
    scheme_size_m: 198,
    member_count: 1800,
    transaction_m: 205,
    status: "Closed to accrual",
  },
  {
    slug: "renishaw",
    display: "Renishaw plc Pension Scheme",
    sector: "Precision Engineering",
    sector_icon: "precision_manufacturing",
    scheme_size_m: 179,
    member_count: 1400,
    transaction_m: 185,
    status: "Closed to new entrants",
  },
  {
    slug: "reading_university",
    display: "University of Reading Pension Scheme",
    sector: "Higher Education",
    sector_icon: "school",
    scheme_size_m: 90,
    member_count: 600,
    transaction_m: 92,
    status: "Closed to accrual",
  },
  {
    slug: "thames_water",
    display: "Thames Water UPS (Closed Section)",
    sector: "Utilities & Infrastructure",
    sector_icon: "water_drop",
    scheme_size_m: 248,
    member_count: 2000,
    transaction_m: 255,
    status: "Closed to new entrants",
  },
  {
    slug: "spirax_sarco",
    display: "Spirax-Sarco Engineering Pension Plan",
    sector: "Industrial Engineering",
    sector_icon: "engineering",
    scheme_size_m: 153,
    member_count: 1100,
    transaction_m: 154,
    status: "Closed to accrual",
  },
  {
    slug: "rsm_uk",
    display: "RSM UK Pension Fund",
    sector: "Professional Services",
    sector_icon: "account_balance",
    scheme_size_m: 108,
    member_count: 900,
    transaction_m: 112,
    status: "Closed to accrual",
  },
];

export function getCustomer(slug: string): CustomerMeta | undefined {
  return CUSTOMERS.find((c) => c.slug === slug);
}
