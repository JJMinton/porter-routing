from simulator.hospital import Hospital


demo1 = Hospital(
    ['lab', 'ward1', 'ward2'], 
    [
        [0, 20, 14],
        [20, 0, 6],
        [14, 6, 0],
    ]
)
demo1.add_porter("Joe")
demo1.add_sample("KGD12", demo1.locations[1], 45)
demo1.add_sample("KGD24", demo1.locations[2], 120)


demo2 = Hospital(
    ['lab', 'ward1', 'ward2' , 'ward3', 'ward4', 'ward5', 'ward6', 'ward7', 'ward8'],
    [
        [0, 548, 776, 696, 582, 274, 502, 194, 308],
        [548, 0, 684, 308, 194, 502, 730, 354, 696],
        [776, 684, 0, 992, 878, 502, 274, 810, 468],
        [696, 308, 992, 0, 114, 650, 878, 502, 844],
        [582, 194, 878, 114, 0, 536, 764, 388, 730],
        [274, 502, 502, 650, 536, 0, 228, 308, 194],
        [502, 730, 274, 878, 764, 228, 0, 536, 194],
        [194, 354, 810, 502, 388, 308, 536, 0, 342],
        [308, 696, 468, 844, 730, 194, 194, 342, 0],
    ],
)
demo2.add_porter("Paul")
demo2.add_porter("Katie")
demo2.add_sample("Sample1", demo2.locations[4], 34)
demo2.add_sample("Sample2", demo2.locations[2], 60)
demo2.add_sample("Sample3", demo2.locations[7], 60)

