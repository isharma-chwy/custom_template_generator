import pandas as pd
import vertica_python
import queries
import logging
from connection_info import conn_info


def get_sql_as_df(query: str) -> pd.DataFrame:
    """Returns a pandas dataframe from a sql query in the queries.py file. Query name must be passed as text. Returns an empty dataframe if the query fails."""
    max_retries = 5
    finished_successfully = False

    for retry in range(max_retries):
        try:
            query_name = getattr(queries, query)
            with vertica_python.connect(**conn_info) as connection:
                db_cursor = connection.cursor('dict')
                db_cursor.execute(query_name)
                template_dict_list = db_cursor.fetchall()
                template_df = pd.DataFrame(template_dict_list)

        except Exception as err:
                logging.error(err)
                if retry == max_retries - 1:
                    logging.error('Max retries reached. Exiting.')
                    return
                
                continue

        else:
            finished_successfully = True
            break

    if not finished_successfully:
        logging.error('Max retries reached. Exiting.')
        return pd.DataFrame()

    return template_df
