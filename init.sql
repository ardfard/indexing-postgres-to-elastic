
CREATE TABLE IF NOT EXISTS public.items (
  item_id serial PRIMARY KEY,
  name VARCHAR (255) NOT NULL,
  stock int8 NOT NULL
);

CREATE TABLE IF NOT EXISTS public.item_prices (
  item_price_id serial PRIMARY KEY,
  item_id bigint,
  unit_price numeric(19,2) NOT NULL
);

CREATE INDEX item_price_item_id ON public.item_prices (
  item_id
);
