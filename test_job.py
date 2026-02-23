from app.models.job import Job

if __name__ == "__main__":
    jpb = Job(priority=1, name="demo", payload="hello world")

    print("Before execution: ")
    print(jpb)

    jpb()

    print("after execution: ")
    print(jpb.status)
    print(jpb.result)
