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

const exactEuros = new Intl.NumberFormat("pt-PT", {
  style: "currency",
  currency: "EUR",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export function formatEuros(cents: number): string {
  const centsInteger = integerCents(cents);
  const roundedEuros = (centsInteger + 50n) / 100n;
  return euros.format(roundedEuros);
}

export function formatEurosExact(cents: number): string {
  const centsInteger = integerCents(cents);
  const wholeEuros = centsInteger / 100n;
  const remainder = (centsInteger % 100n).toString().padStart(2, "0");
  return exactEuros.formatToParts(wholeEuros)
    .map((part) => part.type === "fraction" ? remainder : part.value)
    .join("");
}

function integerCents(cents: number): bigint {
  if (!Number.isSafeInteger(cents) || cents < 0) {
    throw new RangeError("O montante em cêntimos tem de ser um inteiro seguro e não negativo.");
  }
  return BigInt(cents);
}

export function formatPercentage(amountCents: number, totalCents: number): string {
  return percentage.format(totalCents === 0 ? 0 : amountCents / totalCents);
}
