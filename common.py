from pandas import DataFrame
from pandas import concat


def reshape(input_df: DataFrame, x_column: str, y_columns: list[str], y_column_name: str,
            value_column_name: str) -> DataFrame:
    def reshape_helper(input_df_: DataFrame, y_column: str, y_column_name_: str, value_column_name_: str) -> DataFrame:
        output_df = input_df_.rename(columns={y_column: value_column_name_})
        output_df[y_column_name_] = y_column
        return output_df

    result_df = concat([reshape_helper(input_df_=input_df[[x_column, y_column]], y_column=y_column,
                                       y_column_name_=y_column_name, value_column_name_=value_column_name) for y_column
                        in y_columns], ignore_index=True)
    return result_df
