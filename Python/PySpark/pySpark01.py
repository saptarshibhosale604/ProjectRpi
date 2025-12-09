from pyspark.sql import SparkSession
from pyspark.sql.functions import count, avg, round

spark = SparkSession.builder.appName("HR_Analytics").getOrCreate()

print()
print("Department-wise Employee Count and Average Salary: ")
print()

departments = spark.read.csv("Sandbox/DataInput/departments.csv", header=True, inferSchema=True)
employees = spark.read.csv("Sandbox/DataInput/employees.csv", header=True, inferSchema=True)
projects = spark.read.csv("Sandbox/DataInput/projects.csv", header=True, inferSchema=True)

dept_stats = employees.groupBy("dept_id") \
    .agg(count("emp_id").alias("employee_count"), 
         round(avg("salary"), 2).alias("avg_salary")) \
    .join(departments, "dept_id") \
    .select("dept_name", "employee_count", "avg_salary") \
    .orderBy("employee_count", ascending=False)

dept_stats.show()

print()
print("Top 10 Expensive Projects by Department: ")
print()

project_analysis = projects.join(employees, "emp_id") \
    .join(departments, "dept_id") \
    .select("project_id", "project_name", "budget", "dept_name") \
    .orderBy("budget", ascending=False) \
    .limit(10)

project_analysis.show(truncate=False)

