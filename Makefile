test:
	python -m unittest discover test

commit: test
	@git status -s | awk '{print $$2}' > modified_files.txt
	@git add .
	@git commit -m "Modifications: $$(cat modified_files.txt)"
	@git push
	@rm modified_files.txt