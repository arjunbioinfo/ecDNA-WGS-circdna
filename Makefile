.PHONY: help validate ampliconarchitect circle_map_realign circle_map_repeats circexplorer2 clean

help:
	@echo "Targets:"
	@echo "  make validate            # check params + samplesheets are well-formed"
	@echo "  make ampliconarchitect   # WGS amplified-ecDNA (AmpliconArchitect)"
	@echo "  make circle_map_realign  # eccDNA (Circle-Map Realign)"
	@echo "  make circle_map_repeats  # repetitive eccDNA (Circle-Map Repeats)"
	@echo "  make circexplorer2       # circular junctions (CIRCexplorer2)"
	@echo "  make clean               # remove work/ and .nextflow*"

validate:
	python3 ci/validate.py

ampliconarchitect:  ; ./run.sh ampliconarchitect
circle_map_realign: ; ./run.sh circle_map_realign
circle_map_repeats: ; ./run.sh circle_map_repeats
circexplorer2:      ; ./run.sh circexplorer2

clean:
	rm -rf work .nextflow* 
