from asyncio.subprocess import create_subprocess_exec
import psycopg2
from psycopg2 import Error
from faker import Faker
import faker_commerce
import asyncio
import random

fake = Faker()
fake.add_provider(faker_commerce.Provider)


async def createItem(conn):
    while True:
        try:
            name = fake.ecommerce_name()
            stock = random.randint(0, 100)
            price = random.randint(10000, 100000)

            create_item_sql = f"INSERT INTO public.items (name, stock) VALUES ('{name}', {stock}) RETURNING item_id;"
            cursor = conn.cursor()
            cursor.execute(create_item_sql)
            (item_id,) = cursor.fetchone()
            create_item_price_sql = f"INSERT INTO public.item_prices (item_id, unit_price) VALUES ({item_id}, {price});"
            cursor.execute(create_item_price_sql)
            conn.commit()
            print(f"Create item with name={name} stock={stock} price={price}")
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            cursor.close()
            await asyncio.sleep(random.uniform(0.5, 5))


async def updateItem(conn):
    while True:
        await asyncio.sleep(random.uniform(1, 10))
        try:
            cursor = conn.cursor()
            stock = random.randint(0, 100)
            cursor.execute(
                f"SELECT item_id FROM public.items ORDER BY RANDOM() limit 1;"
            )
            (item_id,) = cursor.fetchone()
            cursor.execute(
                f"UPDATE public.items SET stock={stock} where item_id={item_id};"
            )
            conn.commit()
            print(f"Update item with id={item_id} to stock={stock}")
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            cursor.close()


async def updateItemPrice(conn):
    while True:
        await asyncio.sleep(random.uniform(1, 10))
        try:
            cursor = conn.cursor()
            price = random.randint(1000, 100000)
            cursor.execute(
                f"SELECT item_id FROM public.items ORDER BY RANDOM() limit 1;"
            )
            (item_id,) = cursor.fetchone()
            cursor.execute(
                f"UPDATE public.item_prices SET unit_price={price} where item_id={item_id};"
            )
            conn.commit()
            print(f"Update item with id={item_id} to price={price}")
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            cursor.close()


async def main():
    print("Start feeding...")
    try:
        conn = psycopg2.connect(host="localhost", user="postgres", password="testing")
        await asyncio.gather(createItem(conn), updateItem(conn), updateItemPrice(conn))
    except:
        if conn:
            conn.close()


if __name__ == "__main__":
    asyncio.run(main())
