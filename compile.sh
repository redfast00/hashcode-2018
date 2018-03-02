for file in input/*.in
do
  python3 solve.py "$file" "build/$(basename $file .in).out"
done

cp "solve.py" "build/solve.py"
