
function gen(n)
	return coroutine.wrap(function()
		for i=2, n do 
			coroutine.yield(i)
		end
	end)
end

-- filter the numbers generated by `g', removing multiples of `p'
function filter(p, g)
	return coroutine.wrap(function()
		for n in g do
			if n%p ~= 0 then
				coroutine.yield(n) 
			end
		end
	end)
end

N = N or 100			-- from command line
x = gen(N)				-- generate primes up to N
while 1 do
	local n = x()		-- pick a number until done
	if n == nil then 
		break
	end
	print(n)			-- must be a prime number 质数
	x = filter(n, x)	-- now remove its multiples
end