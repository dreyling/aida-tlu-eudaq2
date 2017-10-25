#./euCliReader -i ../../documents/171010_aida-tlu_eudaq2_tests/run_000044_tlu_171011120209.raw -e 1 -E 1091147

./euCliReader -i ../../documents/171010_aida-tlu_eudaq2_tests/run_000044_ni_171011120208.raw -e 1 -E 47750 >> run44_ni.xml

sed -i -e '/Tag/d' -e '1d; $d' -e '1i\<Run>' run44_ni.xml
echo "</Run>" >> run44_ni.xml



return



./euCliReader -i ../../documents/171010_aida-tlu_eudaq2_tests/run_000044_tlu_171011120209.raw -e 1 -E 1000000 > run.xml

#sed -i_bak1 '/Tag/d' run.xml
#sed -i_bak2 '1d; $d' run.xml
#sed -i_bak3 -e '1i\<Run>' run.xml
#echo "</Run>" >> run.xml

sed -i '/Tag/d' run.xml
sed -i '1d; $d' run.xml
sed -i -e '1i\<Run>' run.xml
echo "</Run>" >> run.xml
