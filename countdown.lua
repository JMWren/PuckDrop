function Initialize()
	RELEASETEXT = SELF:GetOption("releasetext")
	MeasureYear = SKIN:GetMeasure('MeasureYear')
	MeasureMonth = SKIN:GetMeasure('MeasureMonth')
	MeasureDay = SKIN:GetMeasure('MeasureDay')
	MeasureHour = SKIN:GetMeasure('MeasureHour')
	MeasureMinute = SKIN:GetMeasure('MeasureMinute')
end

local function to_boolean(str)
	return str == 'True' or str == 'true'
end

function Update()
	local year = MeasureYear:GetValue()
	local month = MeasureMonth:GetValue()
	local day = MeasureDay:GetValue()
	local hour = MeasureHour:GetValue()
	local minute = MeasureMinute:GetValue()
	local dst = SELF:GetOption('IsDST')
	
	if year == 0 or month == 0 or day == 0 then
		return RELEASETEXT
	end

	local timestamp = os.date("!*t")
	timestamp.isdst = to_boolean(dst)

	local epochTimeRemaining = (os.time({year=year, month=month, day=day, hour=hour, min=minute, sec=0})) - os.time(timestamp)

	local timeleft = {
		[1] = math.floor(epochTimeRemaining/60/60/24),	--days
		[2] = math.floor(epochTimeRemaining/60/60)%24,	--hours
		[3] = math.floor(epochTimeRemaining/60)%60,	--minutes
		[4] = math.floor(epochTimeRemaining)%60		--seconds
	}

	local text = {}

	for i=1, #timeleft do
		if i == 1 then
			if timeleft[i] > 0 then
				table.insert(text,timeleft[i])
			end
		else
			if timeleft[i] > 9 then
				table.insert(text,timeleft[i])
			else
				table.insert(text,"0"..timeleft[i])
			end
		end
	end

	if epochTimeRemaining <= 0 or epochTimeRemaining == nil then
		text = RELEASETEXT
	else
		text = table.concat(text,":")
	end

	return tostring(text)
end