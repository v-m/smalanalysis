/*
Testing diffdex code
Author: Vincenzo Musco (http://www.vmusco.com)
*/

public class Foo{
	public void bar(){
		int i = 0;

		if(System.currentTimeMillis() % 2 == 1){
			i += 2;
		}else{
			i += 10;
		}

		i *= 2;
		System.out.println(i);
	}
}
