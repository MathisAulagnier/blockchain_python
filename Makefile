.PHONY: test commit

test:
	python -m unittest discover test

commit: test clean
	@git status -s | awk '{print $$2}' > modified_files.txt
	@git add .
	@git commit -m "Modifications: $$(cat modified_files.txt)"
	@git push
	@rm modified_files.txt

clean:
	rm -rf src/__pycache__/
	rm -rf test/__pycache__/