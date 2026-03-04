from pyspark.sql import SparkSession, Row, functions

def parseInput(line):
    fields = line.split(",")
    return Row(
        id=int(fields[0]),
        name=fields[1],
        age=int(fields[2]),
        city=fields[3]
    )

if __name__ == "__main__":
    print("This module is not meant to be run directly. Please import it as a module in your application.")