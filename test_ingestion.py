from backend.ingestion.clone import clone_repository
from backend.ingestion.reader import read_repository

url = "https://github.com/psf/requests"

print("Cloning repository...")
clone_result = clone_repository(url)

print("\nClone Result:")
print(clone_result)

print("\nReading repository...")
repo_result = read_repository(clone_result.local_path)

print("\nRepository Statistics:")
print(repo_result.stats.to_dict())

print("\nFirst 10 files:")
for file in repo_result.files[:10]:
    print(file.relative_path)