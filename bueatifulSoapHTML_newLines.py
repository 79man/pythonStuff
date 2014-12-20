htmlText = """
<html><head>
<title>Example-Computing Powers</title>
</head>
<body bgcolor="#FFFFFF">
 <a href="../index.html" target="_top"><img src="../icons/cover75.gif" alt="Logo" align="right"></a>
<b>Data Structures and Algorithms 
with Object-Oriented Design Patterns in C++</b><br>
<a name="tex2html2535" href="page53.html"><img alt="next" src="../icons/next_motif.gif" align="BOTTOM" height="24" width="37"></a> <a name="tex2html2533" href="page47.html"><img alt="up" src="../icons/up_motif.gif" align="BOTTOM" height="24" width="26"></a> <a name="tex2html2527" href="page51.html"><img alt="previous" src="../icons/previous_motif.gif" align="BOTTOM" height="24" width="63"></a> <a name="tex2html2537" href="page9.html"><img alt="contents" src="../icons/contents_motif.gif" align="BOTTOM" height="24" width="65"></a> <a name="tex2html2538" href="page620.html"><img alt="index" src="../icons/index_motif.gif" align="BOTTOM" height="24" width="43"></a> <br><hr>
<h2><a name="SECTION003250000000000000000">Example-Computing Powers</a></h2>
<p>
In this section we consider the running time
to raise a number to a given integer power.
I.e., given a value <i>x</i> and non-negative integer <i>n</i>,
we wish to compute the  <img alt="tex2html_wrap_inline58739" src="img159.gif" align="BOTTOM" height="10" width="15">.
A naıve way to calculate  <img alt="tex2html_wrap_inline58739" src="img159.gif" align="BOTTOM" height="10" width="15"> would be to use a loop such as
</p><pre>int result = 1;
for (unsigned int i = 0; i &lt;= n; ++i)
    result *= x;</pre>
While this may be fine for small values of <i>n</i>,
for large values of <i>n</i> the running time may become prohibitive.
As an alternative, consider the following recursive definition
<p><a name="eqnmodelpow">&nbsp;</a> <img alt="equation975" src="img160.gif" align="BOTTOM" height="67" width="500"></p><p>
</p><p>
For example, using Equation&nbsp;<a href="page52.html#eqnmodelpow"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a>,
we would determine  <img alt="tex2html_wrap_inline58751" src="img161.gif" align="BOTTOM" height="12" width="21"> as follows
</p><p> <img alt="displaymath58727" src="img162.gif" align="BOTTOM" height="51" width="337"></p><p>
which requires a total of five multiplication operations.
Similarly, we would compute  <img alt="tex2html_wrap_inline58753" src="img163.gif" align="BOTTOM" height="12" width="21"> as follows
</p><p> <img alt="displaymath58728" src="img164.gif" align="BOTTOM" height="41" width="351"></p><p>
which requires a total of eight multiplication operations.
</p><p>
A recursive algorithm to compute  <img alt="tex2html_wrap_inline58739" src="img159.gif" align="BOTTOM" height="10" width="15">
based on the direct implementation of Equation&nbsp;<a href="page52.html#eqnmodelpow"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a>
is given in Program&nbsp;<a href="page52.html#progpowerc"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a>.
Table&nbsp;<a href="page52.html#tblpowerc"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a> gives the running time,
as predicted by the simplified model,
for each of the executable statements in Program&nbsp;<a href="page52.html#progpowerc"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a>.
</p><p>
</p><p><a name="996">&nbsp;</a><a name="progpowerc">&nbsp;</a> <img alt="program993" src="img165.gif" align="BOTTOM" height="181" width="575"><br>
<strong>Program:</strong> Program to compute  <img alt="tex2html_wrap_inline58739" src="img159.gif" align="BOTTOM" height="10" width="15"><br>
</p><p>
</p><p>
</p><p><a name="1156">&nbsp;</a>
</p><p>
    <a name="tblpowerc">&nbsp;</a>
    </p><div align="CENTER"><p align="CENTER"><table cols="4" frame="HSIDES" rules="GROUPS" border="">
<colgroup><col align="CENTER"><col align="CENTER"><col align="CENTER"><col align="CENTER">
</colgroup><tbody>
<tr><td align="CENTER" nowrap="" valign="BASELINE">
	    </td><td colspan="3" align="CENTER" nowrap="" valign="BASELINE"> time</td></tr>
<tr><td align="CENTER" nowrap="" valign="BASELINE">
<p>
	    statement </p></td><td align="CENTER" nowrap="" valign="BASELINE"> <i>n</i>=0 </td><td align="CENTER" nowrap="" valign="BASELINE"> <i>n</i><i>&gt;</i>0 </td><td align="CENTER" nowrap="" valign="BASELINE"> <i>n</i><i>&gt;</i>0 </td></tr>
<tr><td align="CENTER" nowrap="" valign="BASELINE"> 
	    </td><td align="CENTER" nowrap="" valign="BASELINE"> </td><td align="CENTER" nowrap="" valign="BASELINE"> <i>n</i> is even </td><td align="CENTER" nowrap="" valign="BASELINE"> <i>n</i> is odd </td></tr>
</tbody><tbody>
<tr><td align="CENTER" nowrap="" valign="BASELINE">3 </td><td align="CENTER" nowrap="" valign="BASELINE"> 3 </td><td align="CENTER" nowrap="" valign="BASELINE"> 3 </td><td align="CENTER" nowrap="" valign="BASELINE"> 3 </td></tr>
<tr><td align="CENTER" nowrap="" valign="BASELINE"> 
	    4 </td><td align="CENTER" nowrap="" valign="BASELINE"> 2 </td><td align="CENTER" nowrap="" valign="BASELINE"> -- </td><td align="CENTER" nowrap="" valign="BASELINE"> -- </td></tr>
<tr><td align="CENTER" nowrap="" valign="BASELINE"> 
	    5 </td><td align="CENTER" nowrap="" valign="BASELINE"> -- </td><td align="CENTER" nowrap="" valign="BASELINE"> 5 </td><td align="CENTER" nowrap="" valign="BASELINE"> 5 </td></tr>
<tr><td align="CENTER" nowrap="" valign="BASELINE"> 
	    6 </td><td align="CENTER" nowrap="" valign="BASELINE"> -- </td><td align="CENTER" nowrap="" valign="BASELINE">  <img alt="tex2html_wrap_inline58781" src="img166.gif" align="MIDDLE" height="26" width="96"> </td><td align="CENTER" nowrap="" valign="BASELINE"> -- </td></tr>
<tr><td align="CENTER" nowrap="" valign="BASELINE"> 
	    8 </td><td align="CENTER" nowrap="" valign="BASELINE"> -- </td><td align="CENTER" nowrap="" valign="BASELINE"> -- </td><td align="CENTER" nowrap="" valign="BASELINE">  <img alt="tex2html_wrap_inline58783" src="img167.gif" align="MIDDLE" height="26" width="97"> </td></tr>
</tbody><tbody>
<tr><td align="CENTER" nowrap="" valign="BASELINE">TOTAL </td><td align="CENTER" nowrap="" valign="BASELINE"> 5 </td><td align="CENTER" nowrap="" valign="BASELINE">  <img alt="tex2html_wrap_inline58787" src="img168.gif" align="MIDDLE" height="26" width="96"> </td><td align="CENTER" nowrap="" valign="BASELINE">
		 <img alt="tex2html_wrap_inline58789" src="img169.gif" align="MIDDLE" height="26" width="97"> </td></tr>
</tbody>
<caption align="BOTTOM"><strong>Table:</strong> Computing the running time of Program&nbsp;<a href="page52.html#progpowerc"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a></caption></table>
</p></div><p>
</p><p>
By summing the columns in Table&nbsp;<a href="page52.html#tblpowerc"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a> we get
the following recurrence for the running time of Program&nbsp;<a href="page52.html#progpowerc"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a>
</p><p><a name="eqnmodelpowtime">&nbsp;</a> <img alt="equation1015" src="img170.gif" align="BOTTOM" height="67" width="500"></p><p>
As the first attempt at solving this recurrence,
let us suppose that  <img alt="tex2html_wrap_inline58795" src="img171.gif" align="BOTTOM" height="13" width="45"> for some <i>k</i><i>&gt;</i>0.
Clearly, since <i>n</i> is a power of two, it is even.
Therefore,  <img alt="tex2html_wrap_inline58801" src="img172.gif" align="MIDDLE" height="28" width="137">.
</p><p>
For  <img alt="tex2html_wrap_inline58795" src="img171.gif" align="BOTTOM" height="13" width="45">, Equation&nbsp;<a href="page52.html#eqnmodelpowtime"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a> gives
</p><p> <img alt="displaymath58729" src="img173.gif" align="BOTTOM" height="19" width="358"></p><p>
This can be solved by repeated substitution:
</p><p> <img alt="eqnarray1025" src="img174.gif" align="BOTTOM" height="124" width="500"></p><p>
The substitution stops when <i>k</i>=<i>j</i>.
Thus,
</p><p> <img alt="eqnarray1031" src="img175.gif" align="BOTTOM" height="87" width="500"></p><p>
Note that if  <img alt="tex2html_wrap_inline58795" src="img171.gif" align="BOTTOM" height="13" width="45">, then  <img alt="tex2html_wrap_inline58809" src="img176.gif" align="MIDDLE" height="23" width="68">.
In this case, running time of Program&nbsp;<a href="page52.html#progpowerc"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a>
is  <img alt="tex2html_wrap_inline58811" src="img177.gif" align="MIDDLE" height="24" width="148">.
</p><p>
The preceding result is, in fact, the best case--in all
but the last two recursive calls of the function, <i>n</i> was even.
Interestingly enough, there is a corresponding worst-case scenario.
Suppose  <img alt="tex2html_wrap_inline58815" src="img178.gif" align="MIDDLE" height="24" width="73"> for some value of <i>k</i><i>&gt;</i>0.
Clearly <i>n</i> is odd, since it is one less than  <img alt="tex2html_wrap_inline58821" src="img179.gif" align="BOTTOM" height="13" width="14">
which is a power of two and even.
Now consider  <img alt="tex2html_wrap_inline58823" src="img180.gif" align="MIDDLE" height="26" width="36">:
</p><p> <img alt="eqnarray1034" src="img181.gif" align="BOTTOM" height="62" width="500"></p><p>
Hence,  <img alt="tex2html_wrap_inline58823" src="img180.gif" align="MIDDLE" height="26" width="36"> is also odd!
</p><p>
For example, suppose <i>n</i> is 31 ( <img alt="tex2html_wrap_inline58829" src="img182.gif" align="MIDDLE" height="22" width="40">).
To compute  <img alt="tex2html_wrap_inline58753" src="img163.gif" align="BOTTOM" height="12" width="21">, Program&nbsp;<a href="page52.html#progpowerc"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a> calls itself
recursively to compute  <img alt="tex2html_wrap_inline58833" src="img183.gif" align="BOTTOM" height="12" width="21">,  <img alt="tex2html_wrap_inline58835" src="img184.gif" align="BOTTOM" height="13" width="14">,  <img alt="tex2html_wrap_inline58837" src="img185.gif" align="BOTTOM" height="12" width="15">,  <img alt="tex2html_wrap_inline58839" src="img186.gif" align="BOTTOM" height="12" width="14">, and finally,  <img alt="tex2html_wrap_inline58841" src="img187.gif" align="BOTTOM" height="12" width="15">--all but the last of which are odd powers of <i>x</i>.
</p><p>
For  <img alt="tex2html_wrap_inline58815" src="img178.gif" align="MIDDLE" height="24" width="73">, Equation&nbsp;<a href="page52.html#eqnmodelpowtime"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a> gives
</p><p> <img alt="displaymath58730" src="img188.gif" align="BOTTOM" height="19" width="385"></p><p>
Solving this recurrence by repeated substitution we get
</p><p> <img alt="eqnarray1042" src="img189.gif" align="BOTTOM" height="124" width="500"></p><p>
The substitution stops when <i>k</i>=<i>j</i>.
Thus,
</p><p> <img alt="eqnarray1048" src="img190.gif" align="BOTTOM" height="39" width="500"></p><p>
Note that if  <img alt="tex2html_wrap_inline58815" src="img178.gif" align="MIDDLE" height="24" width="73">, then  <img alt="tex2html_wrap_inline58851" src="img191.gif" align="MIDDLE" height="24" width="105">.
In this case, running time of Program&nbsp;<a href="page52.html#progpowerc"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a>
is  <img alt="tex2html_wrap_inline58853" src="img192.gif" align="MIDDLE" height="24" width="177">.
</p><p>
Consider now what happens for an arbitrary value of <i>n</i>.
Table&nbsp;<a href="page52.html#tblcalls"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a> shows the recursive calls made by
Program&nbsp;<a href="page52.html#progpowerc"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a> in computing  <img alt="tex2html_wrap_inline58739" src="img159.gif" align="BOTTOM" height="10" width="15"> for various values of <i>n</i>.
</p><p>
</p><p><a name="1157">&nbsp;</a>
</p><p>
    <a name="tblcalls">&nbsp;</a>
    </p><div align="CENTER"><p align="CENTER"><table cols="3" frame="HSIDES" rules="GROUPS" border="">
<colgroup><col align="CENTER"><col align="CENTER"><col align="LEFT">
</colgroup><tbody>
<tr><td align="CENTER" nowrap="" valign="BASELINE">
	    <i>n</i> </td><td align="CENTER" nowrap="" valign="BASELINE">  <img alt="tex2html_wrap_inline58863" src="img193.gif" align="MIDDLE" height="26" width="79"> </td><td align="LEFT" nowrap="" valign="BASELINE"> powers computed recursively </td></tr>
</tbody><tbody>
<tr><td align="CENTER" nowrap="" valign="BASELINE">1 </td><td align="CENTER" nowrap="" valign="BASELINE"> 1 </td><td align="LEFT" nowrap="" valign="BASELINE">  <img alt="tex2html_wrap_inline58865" src="img194.gif" align="MIDDLE" height="22" width="22"> </td></tr>
<tr><td align="CENTER" nowrap="" valign="BASELINE"> 
	    2 </td><td align="CENTER" nowrap="" valign="BASELINE"> 2 </td><td align="LEFT" nowrap="" valign="BASELINE">  <img alt="tex2html_wrap_inline58867" src="img195.gif" align="MIDDLE" height="22" width="37"> </td></tr>
<tr><td align="CENTER" nowrap="" valign="BASELINE"> 
	    3 </td><td align="CENTER" nowrap="" valign="BASELINE"> 2 </td><td align="LEFT" nowrap="" valign="BASELINE">  <img alt="tex2html_wrap_inline58869" src="img196.gif" align="MIDDLE" height="22" width="37"> </td></tr>
<tr><td align="CENTER" nowrap="" valign="BASELINE"> 
	    4 </td><td align="CENTER" nowrap="" valign="BASELINE"> 3 </td><td align="LEFT" nowrap="" valign="BASELINE">  <img alt="tex2html_wrap_inline58871" src="img197.gif" align="MIDDLE" height="22" width="53"> </td></tr>
<tr><td align="CENTER" nowrap="" valign="BASELINE"> 
	    5 </td><td align="CENTER" nowrap="" valign="BASELINE"> 3 </td><td align="LEFT" nowrap="" valign="BASELINE">  <img alt="tex2html_wrap_inline58873" src="img198.gif" align="MIDDLE" height="22" width="52"> </td></tr>
<tr><td align="CENTER" nowrap="" valign="BASELINE"> 
	    6 </td><td align="CENTER" nowrap="" valign="BASELINE"> 3 </td><td align="LEFT" nowrap="" valign="BASELINE">  <img alt="tex2html_wrap_inline58875" src="img199.gif" align="MIDDLE" height="22" width="52"> </td></tr>
<tr><td align="CENTER" nowrap="" valign="BASELINE"> 
	    7 </td><td align="CENTER" nowrap="" valign="BASELINE"> 3 </td><td align="LEFT" nowrap="" valign="BASELINE">  <img alt="tex2html_wrap_inline58877" src="img200.gif" align="MIDDLE" height="22" width="52"> </td></tr>
<tr><td align="CENTER" nowrap="" valign="BASELINE"> 
	    8 </td><td align="CENTER" nowrap="" valign="BASELINE"> 4 </td><td align="LEFT" nowrap="" valign="BASELINE">  <img alt="tex2html_wrap_inline58879" src="img201.gif" align="MIDDLE" height="22" width="67"> </td></tr>
</tbody>
<caption align="BOTTOM"><strong>Table:</strong> Recursive calls made in Program&nbsp;<a href="page52.html#progpowerc"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a></caption></table>
</p></div><p>
</p><p>
By inspection we determine that the number of recursive calls made
in which the second argument is non-zero is  <img alt="tex2html_wrap_inline58863" src="img193.gif" align="MIDDLE" height="26" width="79">.
Furthermore, depending on whether the argument is odd or even,
each of these calls contributes either 18 or 20 cycles.
The pattern emerging in Table&nbsp;<a href="page52.html#tblpowerc"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a> suggests that,
on average just as many of the recursive calls result in an even
number as result in an odd one.
The final call (zero argument) adds another 5 cycles.
So, on average, we can expect the running time of Program&nbsp;<a href="page52.html#progpowerc"><img alt="gif" src="../icons/cross_ref_motif.gif" align="BOTTOM"></a>
to be
</p><p><a name="eqnmodelpower">&nbsp;</a> <img alt="equation1072" src="img202.gif" align="BOTTOM" height="16" width="500"></p><p></p>
<hr><a name="tex2html2535" href="page53.html"><img alt="next" src="../icons/next_motif.gif" align="BOTTOM" height="24" width="37"></a> 
<a name="tex2html2533" href="page47.html"><img alt="up" src="../icons/up_motif.gif" align="BOTTOM" height="24" width="26"></a> <a name="tex2html2527" href="page51.html"><img alt="previous" src="../icons/previous_motif.gif" align="BOTTOM" height="24" width="63"></a> <a name="tex2html2537" href="page9.html"><img alt="contents" src="../icons/contents_motif.gif" align="BOTTOM" height="24" width="65"></a> <a name="tex2html2538" href="page620.html"><img alt="index" src="../icons/index_motif.gif" align="BOTTOM" height="24" width="43"></a> <p></p><address>
<img src="../icons/bruno.gif" alt="Bruno" align="right">
<a href="../copyright.html">Copyright © 1997</a> by <a href="../signature.html">Bruno R. Preiss, P.Eng.</a>  All rights reserved.
<a name="1156">&nbsp;</a>
</address>


</body></html>
"""

from bs4.dammit import EntitySubstitution
def uppercase_and_substitute_html_entities(str):
    HTMFormatted = EntitySubstitution.substitute_html(str)
    HTMFormatted = HTMFormatted.replace('\n', '')
    #print "str = [", str, "] HTMFormatted = [", HTMFormatted, "]"
    return HTMFormatted

soupy = BeautifulSoup(htmlText)

sec, footer = soupy.findAll("hr")
if(footer is not None):    
    print "str(footer) = ", str(footer), "BeautifulSoup() = ", BeautifulSoup(str(footer))
    print "----------------------------------------------------------------------------"
    print "footer.prettify() = ", footer.prettify(), "BeautifulSoup() = ", BeautifulSoup(footer.prettify())
    print "----------------------------------------------------------------------------"
    print "footer.prettify(formatter=uppercase_and_substitute_html_entities) = ", footer.prettify(formatter=uppercase_and_substitute_html_entities), "BeautifulSoup() = ", BeautifulSoup(footer.prettify(formatter=uppercase_and_substitute_html_entities))
    print "----------------------------------------------------------------------------"
    footer.extract()
    footerContents = ""
    for tag in footer.findAll() :
        footerContents = footerContents + tag.prettify(formatter=uppercase_and_substitute_html_entities)
    
    print "footerContents = [", footerContents, "]"
    
    chapterTemplate="<html><head><title>{ch_no}. {chapter}</title></head><body><h1>{chapter}</h1>{content}</body></html>"
    
    with open("abcd.html", "w") as fn:
        footerContents = chapterTemplate.format(
            ch_no=100,
            chapter="footer",
            content=footerContents
        )
        fn.write(footerContents)
