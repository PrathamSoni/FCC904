for i in {1..9}; do
  wget https://www2.census.gov/geo/tiger/TIGER2019/BG/tl_2019_0${i}_bg.zip &
done

for i in {10..50}; do
  wget https://www2.census.gov/geo/tiger/TIGER2019/BG/tl_2019_${i}_bg.zip &
done

for i in 51 53 54 55 56 72; do
  wget https://www2.census.gov/geo/tiger/TIGER2019/BG/tl_2019_${i}_bg.zip &
done

wait
unzip '*.zip' -d all_data
rm -f *.zip