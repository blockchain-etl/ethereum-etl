for f in $(find . -name '*.py'); do
#    echo $f
  cat LICENSE.py.template $f > $f.new
  mv $f.new $f
done