for i in {1..9}; do
  wget https://www2.census.gov/geo/tiger/TIGER2020PL/LAYER/BG/2020/tl_2020_0${i}_bg20.zip &
done

for i in {10..50}; do
  wget https://www2.census.gov/geo/tiger/TIGER2020PL/LAYER/BG/2020/tl_2020_${i}_bg20.zip &
done

for i in 51 53 54 55 56 72; do
  wget https://www2.census.gov/geo/tiger/TIGER2020PL/LAYER/BG/2020/tl_2020_${i}_bg20.zip &
done

unzip '*.zip' -d all_data