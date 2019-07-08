Data directory contains test QVD files and their metadata (XML files - metadata was just copied from actual QVD and provided here as example).

These QVDs are used in unit tests.

## tab1.qvd

Contain following simplest table (QlikView script notation):

```
SET NULLINTERPRET =<sym>;
tab1:
LOAD * INLINE [
    ID, NAME, ONEVAL
	123.12,"Pete",0
	124,12/31/2018,0
	-2,"Vaysa",0
	1,"John",0
	<sym>,"None",0
];
store tab1 into "tab1.qvd" (qvd);
```

## tab2.qvd

More lengthy file needed to demostrate multi-byte bit indices:

`tab2:
LOAD * INLINE [
    ID, VAL, NAME, PHONE, SINGLE
	1, 100001, "Pete1", "1234567890", "single value"
	2, 200002, "Pete2", "2234567890", "single value"
	3, 300003, "Pete3", "3234567890", "single value"
	4, 400004, "Pete4", "4234567890", "single value"
	5, 500005, "Pete4", "5234567890", "single value"
	6, 600006, "Pete4", "6234567890", "single value"
	7, 700007, "Pete4", "7234567890", "single value"
	8, 800008, "Pete8", "8234567890", "single value"
	9, 900009, "Pete9", "9234567890", "single value"
	10, 1000000, "Pete10", "02345678910", "single value"
	11, 1000011, "Pete11", "12345678911", "single value"
	12, 2000012, "Pete12", "22345678912", "single value"
	13, 3000013, "Pete13", "32345678913", "single value"
	14, 4000014, "Pete14", "42345678914", "single value"
	15, 5000015, "Pete15", "52345678915", "single value"
	16, 6000016, "Pete16", "62345678916", "single value"
	17, 7000017, "Pete17", "72345678917", "single value"
	-18, <sym>, "Pete17", <sym>, "single value"
	"19", 7000019, -12, -13.4, "single value"
];    

store tab2 into "tab2.qvd" (qvd);
`
