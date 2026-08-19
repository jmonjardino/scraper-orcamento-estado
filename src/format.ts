const euros = new Intl.NumberFormat("pt-PT", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
});

const percentage = new Intl.NumberFormat("pt-PT", {
  style: "percent",
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

export function formatEuros(cents: number): string {
  return euros.format(cents / 100);
}

export function formatPercentage(amountCents: number, totalCents: number): string {
  return percentage.format(totalCents === 0 ? 0 : amountCents / totalCents);
}
