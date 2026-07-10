'' ==========================================================
'' VB1-DOS Clone: FreeBASIC IDE with Frame Container
'' ==========================================================
#include "fbgfx.bi"

Namespace tui

    Function RepeatUTF8(n As Integer, s As String) As String
        Dim res As String = ""
        For i As Integer = 1 To n
            res &= s
        Next
        Return res
    End Function

    '' JSON HELPER FUNCTIONS
    Function JsonEscape(s As String) As String
        Dim result As String = ""
        For i As Integer = 1 To Len(s)
            Dim c As String = Mid(s, i, 1)
            Select Case c
                Case "\": result &= "\\"
                Case """": result &= "\""""
                Case Chr(10): result &= "\n"
                Case Chr(13): ''
                Case Chr(9): result &= "\t"
                Case Else: result &= c
            End Select
        Next
        Return result
    End Function

    Function JsonUnescape(s As String) As String
        Dim result As String = ""
        Dim i As Integer = 1
        While i <= Len(s)
            Dim c As String = Mid(s, i, 1)
            If c = "\" And i < Len(s) Then
                Dim nextc As String = Mid(s, i + 1, 1)
                Select Case nextc
                    Case "\": result &= "\" : i += 1
                    Case """": result &= """" : i += 1
                    Case "n": result &= Chr(10) : i += 1
                    Case "t": result &= Chr(9) : i += 1
                    Case Else: result &= nextc : i += 1
                End Select
            Else
                result &= c
            End If
            i += 1
        Wend
        Return result
    End Function

    Function TrimStr(s As String) As String
        Dim start As Integer = 1
        Dim finish As Integer = Len(s)
        While start <= finish And (Mid(s, start, 1) = " " Or Mid(s, start, 1) = Chr(9))
            start += 1
        Wend
        While finish >= start And (Mid(s, finish, 1) = " " Or Mid(s, finish, 1) = Chr(9))
            finish -= 1
        Wend
        If start > finish Then Return ""
        Return Mid(s, start, finish - start + 1)
    End Function

    Function JsonExtractValue(json As String, key As String) As String
        Dim pattern As String = """" & key & """" & ":"
        Dim pos As Integer = InStr(json, pattern)
        If pos = 0 Then Return ""
        pos += Len(pattern)
        While pos <= Len(json) And (Mid(json, pos, 1) = " " Or Mid(json, pos, 1) = Chr(9))
            pos += 1
        Wend
        Dim startChar As String = Mid(json, pos, 1)
        If startChar = """" Then
            pos += 1
            Dim endPos As Integer = pos
            While endPos <= Len(json)
                If Mid(json, endPos, 1) = """" Then
                    If endPos = Len(json) OrElse Mid(json, endPos + 1, 1) <> "\" Then
                        Return JsonUnescape(Mid(json, pos, endPos - pos))
                    End If
                End If
                endPos += 1
            Wend
        ElseIf startChar = "{" Or startChar = "[" Then
            Dim depth As Integer = 1
            Dim endPos As Integer = pos + 1
            While endPos <= Len(json) And depth > 0
                Dim c As String = Mid(json, endPos, 1)
                If c = """" Then
                    endPos += 1
                    While endPos <= Len(json)
                        If Mid(json, endPos, 1) = """" And Mid(json, endPos - 1, 1) <> "\" Then Exit While
                        endPos += 1
                    Wend
                ElseIf c = startChar Then
                    depth += 1
                ElseIf (startChar = "{" And c = "}") Or (startChar = "[" And c = "]") Then
                    depth -= 1
                End If
                endPos += 1
            Wend
            Return Mid(json, pos, endPos - pos)
        Else
            Dim endPos As Integer = pos
            While endPos <= Len(json)
                Dim c As String = Mid(json, endPos, 1)
                If c = "," Or c = "}" Or c = "]" Then Exit While
                endPos += 1
            Wend
            Return TrimStr(Mid(json, pos, endPos - pos))
        End If
        Return ""
    End Function

    '' WIDGET/CONTROL DATA TYPE
    Type uicontrol
        x As Integer
        y As Integer
        w As Integer
        h As Integer
        tool_type As Integer
        name_id As String
        caption As String
        code As String
        checked As Integer  '' For Check Box and Option Button
        group As String     '' For Option Button mutual exclusion
        parent As Integer   '' For Frame container (0 = no parent)
    End Type

    '' WINDOW CLASS
    Type window
        Declare Constructor(new_x As Integer = 1, new_y As Integer = 1, new_w As Integer = 20, new_h As Integer = 5, new_title As String = "")
        Declare Destructor()
        Declare Sub show(active_ctrl As Integer = 0)
        Declare Sub add_control(cx As Integer, cy As Integer, ctype As Integer, ctitle As String)
        Declare Sub clear_controls()
        Declare Function to_json() As String
        Declare Sub from_json(json As String)
        Declare Function find_control_by_name(name As String) As uicontrol Ptr
        
        Declare Property title As String
        Declare Property title(new_title As String)
        Declare Property x As Integer
        Declare Property x(new_x As Integer)
        Declare Property y As Integer
        Declare Property y(new_y As Integer)
        Declare Property w As Integer
        Declare Property h As Integer
        Declare Property count As Integer
        
    '' MENU ITEM TYPE
    Type menuitem
        caption As String
        name_id As String
        parent As Integer      '' 0 = top-level, otherwise index of parent
        has_submenu As Integer '' 0 = no, 1 = yes
        code As String         '' Event handler code
    End Type

    '' WIDGET/CONTROL DATA TYPE
    Type uicontrol
        x As Integer
        y As Integer
        w As Integer
        h As Integer
        tool_type As Integer
        name_id As String
        caption As String
        code As String
        checked As Integer  '' For Check Box and Option Button
        group As String     '' For Option Button mutual exclusion
        parent As Integer   '' For Frame container (0 = no parent)
        '' List Box and Combo Box properties
        items(1 To 50) As String  '' Items collection
        item_count As Integer      '' Number of items
    '' WINDOW CLASS
    Type window
        Declare Constructor(new_x As Integer = 1, new_y As Integer = 1, new_w As Integer = 20, new_h As Integer = 5, new_title As String = "")
        Declare Destructor()
        Declare Sub show(active_ctrl As Integer = 0)
        Declare Sub add_control(cx As Integer, cy As Integer, ctype As Integer, ctitle As String)
        Declare Sub clear_controls()
        Declare Function to_json() As String
        Declare Sub from_json(json As String)
        Declare Function find_control_by_name(name As String) As uicontrol Ptr
        
        '' Menu functions
        Declare Sub add_menu_item(caption As String, name_id As String, parent_idx As Integer = 0)
        Declare Sub edit_menu()
        Declare Sub draw_menu_bar()
        Declare Function find_menu_item_by_name(name As String) As menuitem Ptr
        
        Declare Property title As String
        Declare Property title(new_title As String)
        Declare Property x As Integer
        Declare Property x(new_x As Integer)
        Declare Property y As Integer
        Declare Property y(new_y As Integer)
        Declare Property w As Integer
        Declare Property h As Integer
        Declare Property count As Integer
        
        Declare Function HitTest(mx As Integer, my As Integer) As Boolean
        Declare Function HitControl(lx As Integer, ly As Integer) As Integer
        Declare Function get_control(idx As Integer) As uicontrol Ptr
        Declare Sub draw_control(idx As Integer, active_ctrl As Integer)

    Private:
        Declare Sub redraw(active_ctrl As Integer = 0)
        Declare Sub remove()
        Declare Sub drawtitle()

        Dim As String mytitle
        Dim As Integer posx, posy, sizew, sizeh
        Dim As uicontrol controls(1 To 30)
    Constructor window(new_x As Integer, new_y As Integer, new_w As Integer, new_h As Integer, new_title As String)
        This.posx = new_x
        This.posy = new_y
        This.sizew = new_w
        This.sizeh = new_h
        This.mytitle = new_title
        This.control_count = 0
        This.menu_count = 0
        If(Len(This.mytitle) = 0) Then This.mytitle = "untitled"
    End Constructor

    Destructor window()
    End Destructor

    Sub window.clear_controls()
        This.control_count = 0
    End Sub
                This.controls(idx).caption = "List"
                '' Add sample items
                This.controls(idx).items(1) = "Item 1"
                This.controls(idx).items(2) = "Item 2"
                This.controls(idx).items(3) = "Item 3"
                This.controls(idx).items(4) = "Item 4"
                This.controls(idx).item_count = 4
            ElseIf ctype = 11 Then  '' Option Button
                This.controls(idx).w = 20
                This.controls(idx).h = 1
                This.controls(idx).caption = "( ) Option"
            ElseIf ctype = 13 Then  '' Text Box
                This.controls(idx).w = 15
                This.controls(idx).h = 1
                This.controls(idx).caption = "Text1"
            Else
                This.controls(idx).w = 12
                This.controls(idx).h = 1
                This.controls(idx).caption = Trim(ctitle)
            End If
            This.redraw()
        End If
    End Sub
            json &= """h"": " & c->h & ", "
            json &= """tool_type"": " & c->tool_type & ", "
            json &= """name_id"": """" & JsonEscape(c->name_id) & """", "
            json &= """caption"": """" & JsonEscape(c->caption) & """", "
            json &= """code"": """" & JsonEscape(c->code) & """"
            json &= "}"
        Next
        json &= "]}"
        Return json
    End Function

    Sub ParseControl(json As String, c As uicontrol Ptr)
        Dim xStr As String = JsonExtractValue(json, "x")
        Dim yStr As String = JsonExtractValue(json, "y")
        Dim wStr As String = JsonExtractValue(json, "w")
        Dim hStr As String = JsonExtractValue(json, "h")
        Dim typeStr As String = JsonExtractValue(json, "tool_type")
        If Len(xStr) > 0 Then c->x = Val(xStr)
        If Len(yStr) > 0 Then c->y = Val(yStr)
        If Len(wStr) > 0 Then c->w = Val(wStr)
        If Len(hStr) > 0 Then c->h = Val(hStr)
        If Len(typeStr) > 0 Then c->tool_type = Val(typeStr)
        c->name_id = JsonExtractValue(json, "name_id")
        c->caption = JsonExtractValue(json, "caption")
        c->code = JsonExtractValue(json, "code")
    End Sub

    Sub window.from_json(json As String)
        This.clear_controls()
        Dim xStr As String = JsonExtractValue(json, "x")
        Dim yStr As String = JsonExtractValue(json, "y")
        Dim wStr As String = JsonExtractValue(json, "w")
        Dim hStr As String = JsonExtractValue(json, "h")
        If Len(xStr) > 0 Then This.posx = Val(xStr)
        If Len(yStr) > 0 Then This.posy = Val(yStr)
        If Len(wStr) > 0 Then This.sizew = Val(wStr)
        If Len(hStr) > 0 Then This.sizeh = Val(hStr)
        Dim newTitle As String = JsonExtractValue(json, "title")
        If Len(newTitle) > 0 Then This.mytitle = newTitle
        
        Dim controlsPos As Integer = InStr(json, """controls""")
        If controlsPos = 0 Then Return
        Dim arrStart As Integer = InStr(controlsPos, json, "[")
        If arrStart = 0 Then Return
        
        Dim depth As Integer = 1
        Dim i As Integer = arrStart + 1
        Dim ctrlStart As Integer = i
        Dim inString As Boolean = False
        
        While i <= Len(json) And depth > 0
            Dim c As String = Mid(json, i, 1)
            If c = """" And (i = 1 OrElse Mid(json, i - 1, 1) <> "\") Then
                inString = Not inString
            ElseIf Not inString Then
                If c = "[" Or c = "{" Then
                    depth += 1
                ElseIf c = "]" Or c = "}" Then
                    depth -= 1
                    If depth = 0 Then Exit While
                ElseIf c = "," And depth = 1 Then
                    Dim ctrlJson As String = Mid(json, ctrlStart, i - ctrlStart)
                    ctrlJson = TrimStr(ctrlJson)
                    If Left(ctrlJson, 1) = "{" Then
                        If This.control_count < 30 Then
                            This.control_count += 1
                            ParseControl(ctrlJson, @This.controls(This.control_count))
                        End If
                    End If
                    ctrlStart = i + 1
                End If
            End If
            i += 1
        Wend
        
        If depth = 0 And ctrlStart < i Then
            Dim lastCtrl As String = Mid(json, ctrlStart, i - ctrlStart - 1)
            lastCtrl = TrimStr(lastCtrl)
            If Left(lastCtrl, 1) = "{" And This.control_count < 30 Then
                This.control_count += 1
                ParseControl(lastCtrl, @This.controls(This.control_count))
            End If
        End If
    End Sub

    Property window.title() As String
        Return This.mytitle
    End Property

    Property window.title(new_title As String)
    Function window.find_control_by_name(name As String) As uicontrol Ptr
        For i As Integer = 1 To This.control_count
            If This.controls(i).name_id = name Then
                Return @This.controls(i)
            End If
        Next
        Return 0
    End Function

    '' ==================== MENU FUNCTIONS ====================
    
    Sub window.add_menu_item(caption As String, name_id As String, parent_idx As Integer = 0)
        If This.menu_count < 50 Then
            This.menu_count += 1
            This.menu_items(This.menu_count).caption = caption
            This.menu_items(This.menu_count).name_id = name_id
            This.menu_items(This.menu_count).parent = parent_idx
            This.menu_items(This.menu_count).has_submenu = 0
            This.menu_items(This.menu_count).code = ""
        End If
    End Sub
    
    Function window.find_menu_item_by_name(name As String) As menuitem Ptr
        For i As Integer = 1 To This.menu_count
            If This.menu_items(i).name_id = name Then
                Return @This.menu_items(i)
            End If
        Next
        Return 0
    End Function
    
    Sub window.draw_menu_bar()
        '' Draw menu bar at top of window
        Color 0, 7
        Locate This.posy + 1, This.posx + 1
        Dim As String menu_line = Space(This.sizew - 2)
        
        '' Collect top-level menu items
        Dim As String menu_text = ""
        For i As Integer = 1 To This.menu_count
            If This.menu_items(i).parent = 0 Then
                If Len(menu_text) > 0 Then menu_text &= "  "
                menu_text &= This.menu_items(i).caption
            End If
        Next
        
        If Len(menu_text) > 0 Then
            menu_line = Left(menu_text & Space(This.sizew - 2), This.sizew - 2)
        End If
        Print menu_line;
    End Sub
    
    Sub window.edit_menu()
        '' Simple menu editor - list existing items and allow adding/editing
        Dim boxW As Integer = 50
        Dim boxH As Integer = 15
        Dim boxX As Integer = (80 - boxW) \ 2
        Dim boxY As Integer = (25 - boxH) \ 2
        
        Dim cursor As Integer = 1
        Dim mode As Integer = 0 '' 0 = view, 1 = add top-level, 2 = add submenu
        
        While 1
            '' Draw box
            Color 15, 0
            Locate boxY, boxX
            Print "┌" & RepeatUTF8(boxW - 2, "─") & "┐";
            For i As Integer = 1 To boxH - 2
                Locate boxY + i, boxX
                Print "│" & Space(boxW - 2) & "│";
    Function window.to_json() As String
        Dim json As String = "{"
        json &= """x"": " & This.posx & ", "
        json &= """y"": " & This.posy & ", "
        json &= """w"": " & This.sizew & ", "
        json &= """h"": " & This.sizeh & ", "
        json &= """title"": """" & JsonEscape(This.mytitle) & """", "
        json &= """menu_count"": " & This.menu_count & ", "
        json &= """menu_items"": ["
        For i As Integer = 1 To This.menu_count
            If i > 1 Then json &= ", "
            json &= "{"
            json &= """caption"": """" & JsonEscape(This.menu_items(i).caption) & """", "
            json &= """name_id"": """" & JsonEscape(This.menu_items(i).name_id) & """", "
            json &= """parent"": " & This.menu_items(i).parent & ", "
            json &= """has_submenu"": " & This.menu_items(i).has_submenu
            json &= "}"
        Next
        json &= "], "
        json &= """controls"": ["
        For i As Integer = 1 To This.control_count
            If i > 1 Then json &= ", "
            Dim c As uicontrol Ptr = @This.controls(i)
            json &= "{"
            json &= """x"": " & c->x & ", "
            json &= """y"": " & c->y & ", "
            json &= """w"": " & c->w & ", "
            json &= """h"": " & c->h & ", "
            json &= """tool_type"": " & c->tool_type & ", "
            json &= """name_id"": """" & JsonEscape(c->name_id) & """", "
            json &= """caption"": """" & JsonEscape(c->caption) & """", "
            json &= """code"": """" & JsonEscape(c->code) & """"
            json &= "}"
        Next
        json &= "]}"
        Return json
    End Function
                        If This.menu_count > 0 And cursor <= This.menu_count Then
                            '' Ask if this should be a submenu
                            If This.menu_items(cursor).parent = 0 Then
    Sub ParseMenuItem(json As String, m As menuitem Ptr)
        m->caption = JsonExtractValue(json, "caption")
        m->name_id = JsonExtractValue(json, "name_id")
        Dim parentStr As String = JsonExtractValue(json, "parent")
        Dim subStr As String = JsonExtractValue(json, "has_submenu")
        If Len(parentStr) > 0 Then m->parent = Val(parentStr)
        If Len(subStr) > 0 Then m->has_submenu = Val(subStr)
        m->code = ""
    End Sub

    Sub window.from_json(json As String)
        This.clear_controls()
        This.menu_count = 0
        
        Dim xStr As String = JsonExtractValue(json, "x")
        Dim yStr As String = JsonExtractValue(json, "y")
        Dim wStr As String = JsonExtractValue(json, "w")
        Dim hStr As String = JsonExtractValue(json, "h")
        If Len(xStr) > 0 Then This.posx = Val(xStr)
        If Len(yStr) > 0 Then This.posy = Val(yStr)
        If Len(wStr) > 0 Then This.sizew = Val(wStr)
        If Len(hStr) > 0 Then This.sizeh = Val(hStr)
        Dim newTitle As String = JsonExtractValue(json, "title")
        If Len(newTitle) > 0 Then This.mytitle = newTitle
        
        '' Parse menu items
        Dim menuPos As Integer = InStr(json, """menu_items""")
        If menuPos > 0 Then
            Dim menuArrStart As Integer = InStr(menuPos, json, "[")
            If menuArrStart > 0 Then
                Dim depth As Integer = 1
                Dim i As Integer = menuArrStart + 1
                Dim itemStart As Integer = i
                Dim inStr As Boolean = False
                
                While i <= Len(json) And depth > 0
                    Dim c As String = Mid(json, i, 1)
                    If c = """" And (i = 1 OrElse Mid(json, i - 1, 1) <> "\") Then
                        inStr = Not inStr
                    ElseIf Not inStr Then
                        If c = "[" Or c = "{" Then
                            depth += 1
                        ElseIf c = "]" Or c = "}" Then
                            depth -= 1
                            If depth = 0 Then Exit While
                        ElseIf c = "," And depth = 1 Then
                            Dim itemJson As String = Mid(json, itemStart, i - itemStart)
                            itemJson = TrimStr(itemJson)
                            If Left(itemJson, 1) = "{" Then
                                If This.menu_count < 50 Then
                                    This.menu_count += 1
                                    ParseMenuItem(itemJson, @This.menu_items(This.menu_count))
                                End If
                            End If
                            itemStart = i + 1
                        End If
                    End If
                    i += 1
                Wend
                
                '' Last item
                If depth = 0 And itemStart < i Then
                    Dim lastItem As String = Mid(json, itemStart, i - itemStart - 1)
                    lastItem = TrimStr(lastItem)
                    If Left(lastItem, 1) = "{" And This.menu_count < 50 Then
                        This.menu_count += 1
                        ParseMenuItem(lastItem, @This.menu_items(This.menu_count))
                    End If
                End If
            End If
        End If
        
        '' Parse controls
        Dim controlsPos As Integer = InStr(json, """controls""")
        If controlsPos = 0 Then Return
        Dim arrStart As Integer = InStr(controlsPos, json, "[")
        If arrStart = 0 Then Return
    End Function

    Sub window.show(active_ctrl As Integer = 0)
        This.redraw(active_ctrl)
    End Sub

    Sub window.drawtitle()
        Color 15, 1
        Locate This.posy, This.posx + (This.sizew \ 2) - (Len(This.mytitle) \ 2) - 1
        Print " " & This.mytitle & " ";
    End Sub

    Sub window.remove()
        Color 7, 0
        Var spaces = Space(This.sizew)
        For i As Integer = This.posy To This.posy + This.sizeh - 1
            Locate i, This.posx
            Print spaces;
        Next
    End Sub

    Sub window.draw_control(idx As Integer, active_ctrl As Integer)
        Dim As Integer draw_y = This.posy + This.controls(idx).y
        Dim As Integer draw_x = This.posx + This.controls(idx).x
        Dim As String cap = This.controls(idx).caption
        Dim As Integer wid = This.controls(idx).w
        Dim As Integer hgt = This.controls(idx).h
        
        '' Clip to parent frame if any
        If This.controls(idx).parent > 0 And This.controls(idx).parent <= This.control_count Then
            Dim As Integer px = This.controls(This.controls(idx).parent).x
            Dim As Integer py = This.controls(This.controls(idx).parent).y
            Dim As Integer pw = This.controls(This.controls(idx).parent).w
            Dim As Integer ph = This.controls(This.controls(idx).parent).h
            '' Simple clipping: don't draw if outside parent bounds
    Sub window.redraw(active_ctrl As Integer = 0)
        Color 15, 1
        Locate This.posy, This.posx
        Print "┌" & RepeatUTF8(This.sizew - 2, "─") & "┐";
        For i As Integer = This.posy + 1 To This.posy + This.sizeh - 2
            Locate i, This.posx
            Color 15, 1: Print "│";
            Color 8, 7:  Print Space(This.sizew - 2);
            Color 15, 1: Print "│";
        Next
        Locate This.posy + This.sizeh - 1, This.posx
        Print "└" & RepeatUTF8(This.sizew - 2, "─") & "┘";
        This.drawtitle()
        
        '' Draw menu bar if menu items exist
        If This.menu_count > 0 Then
            This.draw_menu_bar()
        End If
        
        '' First pass: draw containers (Frames) in order
        For i As Integer = 1 To This.control_count
            If This.controls(i).tool_type = 7 Then
                This.draw_control(i, active_ctrl)
            End If
        Next
            If Len(cap) > 0 Then
                Locate draw_y, draw_x + 2
                Print " " & cap & " ";
            End If
        ElseIf This.controls(idx).tool_type = 11 Then
            '' Option Button (*) or ( )
            Color 0, 7
            Locate draw_y, draw_x
            Dim optState As String = "( )"
            If This.controls(idx).checked <> 0 Then optState = "(*)"
            Dim labelText As String = cap
            If Left(cap, 3) = "( )" Or Left(cap, 3) = "(*)" Then labelText = Mid(cap, 4)
            Print optState & labelText;
        ElseIf This.controls(idx).tool_type = 13 Then
            Color 0, 3
            For r As Integer = 0 To hgt - 1
                Locate draw_y + r, draw_x
                If r = 0 Then
                    Dim As String txt_text = Space(wid - Len(cap)) & cap
                    Print Right(Space(wid) & txt_text, wid);
                Else
                    Print Space(wid);
                End If
            Next
        Else
            Color 0, 3
            For r As Integer = 0 To hgt - 1
                Locate draw_y + r, draw_x
                If r = 0 Then
                    Print Left(cap & Space(wid), wid);
                Else
                    Print Space(wid);
                End If
            Next
        End If
    End Sub

    Sub window.redraw(active_ctrl As Integer = 0)
        Color 15, 1
        Locate This.posy, This.posx
        Print "┌" & RepeatUTF8(This.sizew - 2, "─") & "┐";
        For i As Integer = This.posy + 1 To This.posy + This.sizeh - 2
            Locate i, This.posx
            Color 15, 1: Print "│";
            Color 8, 7:  Print Space(This.sizew - 2);
            Color 15, 1: Print "│";
        Next
        Locate This.posy + This.sizeh - 1, This.posx
        Print "└" & RepeatUTF8(This.sizew - 2, "─") & "┘";
        This.drawtitle()
        
        '' First pass: draw containers (Frames) in order
        For i As Integer = 1 To This.control_count
        ElseIf This.controls(idx).tool_type = 7 Then
            '' Frame container
            Color 15, 1
            Locate draw_y, draw_x
            Print "┌" & RepeatUTF8(wid - 2, "─") & "┐";
            For r As Integer = 1 To hgt - 2
                Locate draw_y + r, draw_x
                Print "│" & Space(wid - 2) & "│";
            Next
            Locate draw_y + hgt - 1, draw_x
            Print "└" & RepeatUTF8(wid - 2, "─") & "┘";
            '' Draw caption
            If Len(cap) > 0 Then
                Locate draw_y, draw_x + 2
                Print " " & cap & " ";
            End If
        ElseIf This.controls(idx).tool_type = 10 Then
            '' List Box with scrollbar
            Color 0, 7
            '' Draw border
            Locate draw_y, draw_x
            Print "┌" & RepeatUTF8(wid - 3, "─") & "┬┐";
            '' Draw items
            Dim As Integer visible_rows = hgt - 2
            For r As Integer = 0 To visible_rows - 1
                Locate draw_y + 1 + r, draw_x
                Dim As Integer item_idx = This.controls(idx).scroll_offset + r + 1
                If item_idx <= This.controls(idx).item_count Then
                    Dim As String item_text = This.controls(idx).items(item_idx)
                    If Len(item_text) > wid - 4 Then
                        item_text = Left(item_text, wid - 4)
                    End If
                    '' Highlight selected item
                    If item_idx - 1 = This.controls(idx).selected_index Then
                        Color 15, 3  '' White on cyan (highlight)
                    Else
                        Color 0, 7
                    End If
                    Print "│ " & Left(item_text & Space(wid - 4), wid - 4);
                    Color 0, 7
                    Print "││";
                Else
                    Color 0, 7
                    Print "│" & Space(wid - 3) & "││";
                End If
            Next
            '' Draw bottom border
            Locate draw_y + hgt - 1, draw_x
            Print "└" & RepeatUTF8(wid - 3, "─") & "┴┘";
            '' Draw scrollbar
            If This.controls(idx).item_count > visible_rows Then
                Dim As Integer sb_height = visible_rows
                Dim As Integer thumb_size = Max(1, (visible_rows * sb_height) \ This.controls(idx).item_count)
                Dim As Integer thumb_pos = (This.controls(idx).scroll_offset * (sb_height - thumb_size)) \ (This.controls(idx).item_count - visible_rows)
                For r As Integer = 0 To sb_height - 1
                    Locate draw_y + 1 + r, draw_x + wid - 1
                    If r >= thumb_pos And r < thumb_pos + thumb_size Then
                        Print "█";
                    Else
                        Print "░";
                    End If
                Next
            End If
        ElseIf This.controls(idx).tool_type = 2 Then
            '' Combo Box (dropdown)
            Color 0, 7
            Locate draw_y, draw_x
            Dim As String display_text = cap
            If This.controls(idx).selected_index >= 0 And This.controls(idx).selected_index < This.controls(idx).item_count Then
                display_text = This.controls(idx).items(This.controls(idx).selected_index + 1)
            End If
            If Len(display_text) > wid - 4 Then
                display_text = Left(display_text, wid - 4)
            End If
            Print " " & Left(display_text & Space(wid - 4), wid - 4) & " ▼";
        ElseIf This.controls(idx).tool_type = 11 Then

    Sub Toolbox.remove()
        Color 7, 0
        Var spaces = Space(This.w)
        For i As Integer = This.y To This.y + This.h - 1
            Locate i, This.x
            Print spaces;
        Next
    End Sub

    Sub Toolbox.draw()
        Color 0, 3
        Locate This.y, This.x
        Print "┌" & RepeatUTF8(This.w - 2, "─") & "┐";
        Locate This.y, This.x + (This.w \ 2) - 3
        Print "-Tools-";
        Dim As Integer current_y = This.y + 1
        Locate current_y, This.x
        Print "│";
        If This.active_tool = 0 Then Color 3, 0 Else Color 0, 3
        Print Left(This.items(0) & Space(This.w - 2), This.w - 2);
        Color 0, 3
        Print "│";
        current_y += 1
        Locate current_y, This.x
        Print "├" & RepeatUTF8(This.w - 2, "─") & "┤";
        current_y += 1
        For i As Integer = 1 To 15
            Locate current_y, This.x
            Print "│";
            If This.active_tool = i Then Color 3, 0 Else Color 0, 3
            Print Left(This.items(i) & Space(This.w - 2), This.w - 2);
            Color 0, 3
            Print "│";
            current_y += 1
        Next
        Locate current_y, This.x
        Print "└" & RepeatUTF8(This.w - 2, "─") & "┘";
    End Sub

    Function Toolbox.process_click(mx As Integer, my As Integer) As Boolean
        If mx >= This.x And mx < This.x + This.w Then
            If my = This.y + 1 Then
                This.active_tool = 0
                Return True
            ElseIf my >= This.y + 3 And my <= This.y + 17 Then
                This.active_tool = my - (This.y + 2)
                Return True
            End If
        End If
        Return False
    End Function

    '' DIALOG FUNCTIONS
    Sub ShowMessageBox(msg As String, title As String = "Message")
        Dim msgLines(1 To 10) As String
        Dim lineCount As Integer = 0
        Dim startPos As Integer = 1
        For i As Integer = 1 To Len(msg)
            If Mid(msg, i, 1) = Chr(10) Or i = Len(msg) Then
                If i = Len(msg) Then i += 1
                lineCount += 1
                If lineCount <= 10 Then
                    msgLines(lineCount) = Mid(msg, startPos, i - startPos)
                End If
                startPos = i + 1
            End If
        Next
        If lineCount = 0 Then
            lineCount = 1
            msgLines(1) = msg
        End If
        Dim maxLen As Integer = Len(title)
        For i As Integer = 1 To lineCount
            If Len(msgLines(i)) > maxLen Then maxLen = Len(msgLines(i))
        Next
        If maxLen < 20 Then maxLen = 20
        Dim boxW As Integer = maxLen + 4
        Dim boxH As Integer = lineCount + 4
        Dim boxX As Integer = (80 - boxW) \ 2
        Dim boxY As Integer = (25 - boxH) \ 2
        
        Color 15, 1
        Locate boxY, boxX
        Print "┌" & RepeatUTF8(boxW - 2, "─") & "┐";
        For i As Integer = 1 To boxH - 2
            Locate boxY + i, boxX
            Print "│" & Space(boxW - 2) & "│";
        Next
        Locate boxY + boxH - 1, boxX
        Print "└" & RepeatUTF8(boxW - 2, "─") & "┘";
        Color 15, 1
        Locate boxY, boxX + (boxW - Len(title)) \ 2
        Print " " & title & " ";
        Color 15, 1
        For i As Integer = 1 To lineCount
            Locate boxY + 1 + i, boxX + 2
            Print msgLines(i);
        Next
        Color 0, 7
        Locate boxY + boxH - 2, boxX + (boxW - 6) \ 2
        Print "[ OK ]";
        Dim k As String
        Do
            k = Inkey()
            Sleep 10, 1
        Loop Until k <> "" Or MultiKey(1)
    End Sub

    Function PromptInput(prompt As String, defaultVal As String = "") As String
        Dim boxW As Integer = 50
        Dim boxH As Integer = 5
        Dim boxX As Integer = (80 - boxW) \ 2
        Dim boxY As Integer = (25 - boxH) \ 2
    Function EditCode(target_name As String, initial_code As String, event_type As String = "click") As String
        Dim lines(1 To 100) As String
        Dim lineCount As Integer = 0
        SplitLines(initial_code, lines(), lineCount)
        If lineCount = 0 Then
            '' Generate appropriate template based on event type
            Dim template As String
            Select Case event_type
                Case "change"
                    template = "Sub on_change_" & target_name & "()_" & Chr(10) & _
                              "    '' Called when text changes" & Chr(10) & _
                              "    '' Access text with: control_name.caption" & Chr(10) & _
                              "End Sub"
                Case "focus"
                    template = "Sub on_focus_" & target_name & "()_" & Chr(10) & _
                              "    '' Called when control receives focus" & Chr(10) & _
                              "End Sub"
                Case "blur"
                    template = "Sub on_blur_" & target_name & "()_" & Chr(10) & _
                              "    '' Called when control loses focus" & Chr(10) & _
                              "End Sub"
                Case "timer"
                    template = "Sub on_timer_" & target_name & "()_" & Chr(10) & _
                              "    '' Called on each timer interval" & Chr(10) & _
                              "    '' Use msgbox to debug: msgbox ""Timer tick!""" & Chr(10) & _
                              "End Sub"
                Case "load"
                    template = "Sub on_load_" & target_name & "()_" & Chr(10) & _
                              "    '' Called when form loads" & Chr(10) & _
                              "    '' Initialize controls here" & Chr(10) & _
                              "End Sub"
                Case Else
                    template = "Sub on_click_" & target_name & "()_" & Chr(10) & _
                              "    '' Your code here" & Chr(10) & _
                              "    msgbox ""Hello from " & target_name & "!""" & Chr(10) & _
                              "End Sub"
            End Select
            
            '' Split template into lines
            Dim tempStart As Integer = 1
            For i As Integer = 1 To Len(template)
                If Mid(template, i, 1) = "_" Then
                    lineCount += 1
                    lines(lineCount) = Mid(template, tempStart, i - tempStart)
                    tempStart = i + 1
                End If
            Next
        End If
        Dim cursorX As Integer = 1
        Dim cursorY As Integer = 1
        Dim scrollY As Integer = 0
        Dim boxW As Integer = 60
        Dim boxH As Integer = 15
        Dim boxX As Integer = (80 - boxW) \ 2
        Dim boxY As Integer = (25 - boxH) \ 2
        While 1
            Color 15, 0
            Locate boxY, boxX
            Print "┌" & RepeatUTF8(boxW - 2, "─") & "┐";
            For i As Integer = 1 To boxH - 2
                Locate boxY + i, boxX
                Print "│" & Space(boxW - 2) & "│";
            Next
            Locate boxY + boxH - 1, boxX
            Print "└" & RepeatUTF8(boxW - 2, "─") & "┘";
            Color 15, 0
            Locate boxY, boxX + 2
            Print " Code: " & target_name & " (" & event_type & ") ";
            Locate boxY, boxX + boxW - 4
            Print "[X]";
            Color 8, 7
            Locate boxY + boxH - 1, boxX + 2
            Print " ESC=Cancel | ENTER=Save | Arrow keys=Move ";
            Dim visibleLines As Integer = boxH - 3
            For i As Integer = 1 To visibleLines
                Dim lineIdx As Integer = scrollY + i
                Locate boxY + i, boxX + 1
                Color 0, 7
                If lineIdx <= lineCount Then
                    Dim displayLine As String = lines(lineIdx)
                    If Len(displayLine) > boxW - 2 Then
                        displayLine = Left(displayLine, boxW - 2)
                    End If
                    displayLine = displayLine & Space(boxW - 2 - Len(displayLine))
                    Print displayLine;
                Else
                    Print Space(boxW - 2);
                End If
            Next
            Dim screenX As Integer = boxX + cursorX
            Dim screenY As Integer = boxY + cursorY - scrollY
            If screenY >= boxY + 1 And screenY <= boxY + boxH - 2 Then
                Locate screenY, screenX, 1
            End If
            Dim k As String = Inkey()
            If k = Chr(27) Then
                Return initial_code
            ElseIf k = Chr(13) Then
                Return JoinLines(lines(), lineCount)
            ElseIf k = Chr(9) Then
                If cursorY <= lineCount Then
                    Dim before As String = Left(lines(cursorY), cursorX - 1)
                    Dim after As String = Mid(lines(cursorY), cursorX)
                    lines(cursorY) = before & "    " & after
                    cursorX += 4
                End If
            ElseIf k = Chr(8) Then
                If cursorX > 1 Then
                    Dim before As String = Left(lines(cursorY), cursorX - 2)
                    Dim after As String = Mid(lines(cursorY), cursorX)
                    lines(cursorY) = before & after
                    cursorX -= 1
                ElseIf cursorY > 1 Then
                    cursorX = Len(lines(cursorY - 1)) + 1
                    lines(cursorY - 1) = lines(cursorY - 1) & lines(cursorY)
                    For i As Integer = cursorY To lineCount - 1
                        lines(i) = lines(i + 1)
                    Next
                    lineCount -= 1
                    cursorY -= 1
                End If
            ElseIf k = Chr(255) & "K" Then
                If cursorX > 1 Then
                    cursorX -= 1
                ElseIf cursorY > 1 Then
                    cursorY -= 1
                    cursorX = Len(lines(cursorY)) + 1
                End If
            ElseIf k = Chr(255) & "M" Then
                If cursorY <= lineCount And cursorX <= Len(lines(cursorY)) Then
                    cursorX += 1
                ElseIf cursorY < lineCount Then
                    cursorY += 1
                    cursorX = 1
                End If
            ElseIf k = Chr(255) & "H" Then
                If cursorY > 1 Then
                    cursorY -= 1
                    If cursorX > Len(lines(cursorY)) + 1 Then
                        cursorX = Len(lines(cursorY)) + 1
                    End If
                    If cursorY <= scrollY Then scrollY = cursorY - 1
                End If
            ElseIf k = Chr(255) & "P" Then
                If cursorY < lineCount Then
                    cursorY += 1
                    If cursorX > Len(lines(cursorY)) + 1 Then
                        cursorX = Len(lines(cursorY)) + 1
                    End If
                    If cursorY > scrollY + visibleLines Then scrollY = cursorY - visibleLines
                End If
            ElseIf Len(k) = 1 And Asc(k) >= 32 And Asc(k) <= 126 Then
                If cursorY <= lineCount Then
                    Dim before As String = Left(lines(cursorY), cursorX - 1)
                    Dim after As String = Mid(lines(cursorY), cursorX)
                    lines(cursorY) = before & k & after
                    cursorX += 1
                End If
            ElseIf k = Chr(255) & "S" Then
                If cursorY <= lineCount Then
    Sub ExecuteEvent(eventName As String, formWin As window Ptr)
        '' Support multiple event types: on_click, on_change, on_focus, on_blur, on_timer, on_load, on_menu
        Dim eventPrefix As String = ""
        Dim controlName As String = ""
        
        '' Extract event type and control name from eventName
        If Left(LCase(eventName), 8) = "on_click" Then
            eventPrefix = "on_click"
            controlName = Mid(eventName, 10)
        ElseIf Left(LCase(eventName), 9) = "on_change" Then
            eventPrefix = "on_change"
            controlName = Mid(eventName, 11)
        ElseIf Left(LCase(eventName), 8) = "on_focus" Then
            eventPrefix = "on_focus"
            controlName = Mid(eventName, 10)
        ElseIf Left(LCase(eventName), 7) = "on_blur" Then
            eventPrefix = "on_blur"
            controlName = Mid(eventName, 9)
        ElseIf Left(LCase(eventName), 8) = "on_timer" Then
            eventPrefix = "on_timer"
            controlName = Mid(eventName, 10)
        ElseIf Left(LCase(eventName), 7) = "on_load" Then
            eventPrefix = "on_load"
            controlName = Mid(eventName, 9)
        ElseIf Left(LCase(eventName), 7) = "on_menu" Then
            eventPrefix = "on_menu"
            controlName = Mid(eventName, 9)
        Else
            controlName = eventName
        End If
        
        '' Search in controls
        For i As Integer = 1 To formWin->count
            Dim c As uicontrol Ptr = formWin->get_control(i)
            If c <> 0 And Len(c->code) > 0 Then
                '' Check if code contains the event handler
                If InStr(LCase(c->code), LCase(eventName)) > 0 Then
                    Dim lines(1 To 100) As String
                    Dim lineCount As Integer = 0
                    SplitLines(c->code, lines(), lineCount)
                    Dim inSub As Boolean = False
                    For j As Integer = 1 To lineCount
                        Dim line As String = TrimStr(lines(j))
                        If Len(line) = 0 Then Continue For
                        If Left(LCase(line), 3) = "sub" Then
                            If InStr(LCase(line), LCase(eventName)) > 0 Then
                                inSub = True
                                Continue For
                            End If
                        ElseIf LCase(line) = "end sub" Then
                            inSub = False
                        ElseIf inSub Then
                            ExecuteLine(line, formWin)
                        End If
                    Next
                End If
            End If
        Next
        
        '' Also check menu items for menu events
        For i As Integer = 1 To formWin->menu_count
            If Len(formWin->menu_items(i).code) > 0 Then
                If InStr(LCase(formWin->menu_items(i).code), LCase(eventName)) > 0 Then
                    Dim lines(1 To 100) As String
                    Dim lineCount As Integer = 0
                    SplitLines(formWin->menu_items(i).code, lines(), lineCount)
                    Dim inSub As Boolean = False
                    For j As Integer = 1 To lineCount
                        Dim line As String = TrimStr(lines(j))
                        If Len(line) = 0 Then Continue For
                        If Left(LCase(line), 3) = "sub" Then
                            If InStr(LCase(line), LCase(eventName)) > 0 Then
                                inSub = True
                                Continue For
                            End If
                        ElseIf LCase(line) = "end sub" Then
                            inSub = False
                        ElseIf inSub Then
                            ExecuteLine(line, formWin)
                        End If
                    Next
                End If
            End If
        Next
    End Sub

End Namespace
                End If
                startPos = i + 1
            End If
        Next
        If startPos <= Len(src) Then
            count += 1
            If count <= UBound(lines) Then
                lines(count) = Mid(src, startPos)
            End If
        End If
        If count = 0 And Len(src) > 0 Then
            count = 1
            lines(1) = src
                                If run_mode Then
                                    '' Check if clicked on menu bar first
                                    If local_y = 1 And windows(i)->menu_count > 0 Then
                                        Dim As Integer menu_x = 1
                                        For m As Integer = 1 To windows(i)->menu_count
                                            If windows(i)->menu_items(m).parent = 0 Then
                                                Dim As Integer item_w = Len(windows(i)->menu_items(m).caption) + 2
                                                If local_x >= menu_x And local_x < menu_x + item_w Then
                                                    Dim eventName As String = "on_menu_" & windows(i)->menu_items(m).name_id
                                                    tui.ExecuteEvent(eventName, windows(i))
                                                    clicked_handled = True
                                                    Exit For
                                                End If
                                                menu_x += item_w + 2
                                            End If
                                        Next
                                        If clicked_handled Then Exit For
                                    End If
                                    
                                    Dim As Integer clicked_ctrl = windows(i)->HitControl(local_x, local_y)
                                    If clicked_ctrl > 0 Then
                                        Dim As tui.uicontrol Ptr c = windows(i)->get_control(clicked_ctrl)
                                        If c <> 0 Then
                                            '' Track focus changes
                                            Static last_focused_ctrl As Integer = 0
                                            If clicked_ctrl <> last_focused_ctrl Then
                                                '' Fire on_blur for previously focused control
                                                If last_focused_ctrl > 0 Then
                                                    Dim As tui.uicontrol Ptr last_c = windows(i)->get_control(last_focused_ctrl)
                                                    If last_c <> 0 Then
                                                        Dim blurEvent As String = "on_blur_" & last_c->name_id
                                                        tui.ExecuteEvent(blurEvent, windows(i))
                                                    End If
                                                End If
                                                '' Fire on_focus for newly focused control
                                                Dim focusEvent As String = "on_focus_" & c->name_id
                                                tui.ExecuteEvent(focusEvent, windows(i))
                                                last_focused_ctrl = clicked_ctrl
                                            End If
                                            
                                            If c->tool_type = 1 Then
                                                '' Toggle Check Box
                                                c->checked = Not c->checked
                                                Dim changeEvent As String = "on_change_" & c->name_id
                                                tui.ExecuteEvent(changeEvent, windows(i))
                                                windows(1)->show()
                                            ElseIf c->tool_type = 2 Then
                                                '' Combo Box - cycle through items
                                                c->selected_index += 1
                                                If c->selected_index >= c->item_count Then
                                                    c->selected_index = 0
                                                End If
                                                Dim changeEvent As String = "on_change_" & c->name_id
                                                tui.ExecuteEvent(changeEvent, windows(i))
                                                windows(1)->show()
                                            ElseIf c->tool_type = 3 Then
                                                Dim eventName As String = "on_click_" & c->name_id
                                                tui.ExecuteEvent(eventName, windows(i))
                                                windows(1)->show()
                                            ElseIf c->tool_type = 10 Then
                                                '' List Box - select item
                                                Dim As Integer rel_y = local_y - c->y - 1
                                                Dim As Integer item_idx = c->scroll_offset + rel_y
                                                If item_idx >= 0 And item_idx < c->item_count Then
                                                    c->selected_index = item_idx
                                                    Dim changeEvent As String = "on_change_" & c->name_id
                                                    tui.ExecuteEvent(changeEvent, windows(i))
                                                End If
                                                windows(1)->show()
                                            ElseIf c->tool_type = 11 Then
                                                '' Option Button - uncheck others in same group
                                                c->checked = 1
                                                For j As Integer = 1 To windows(i)->count
                                                    Dim As tui.uicontrol Ptr other = windows(i)->get_control(j)
                                                    If other <> 0 And other->tool_type = 11 And other <> c Then
                                                        If other->group = c->group Then
                                                            other->checked = 0
                                                        End If
                                                    End If
                                                Next
                                                Dim changeEvent As String = "on_change_" & c->name_id
                                                tui.ExecuteEvent(changeEvent, windows(i))
                                                windows(1)->show()
                                            ElseIf c->tool_type = 13 Then
                                                '' Text Box - just focus, on_change fires on text edit
                                                run_focused_ctrl = clicked_ctrl
                                            ElseIf c->tool_type = 14 Then
                                                '' Timer - toggle enabled
                                                '' Timer events are handled separately in the main loop
                                            End If
                                        End If
                                    End If
            ElseIf k = Chr(8) Then
                If cursorX > 1 Then
                    Dim before As String = Left(lines(cursorY), cursorX - 2)
                    Dim after As String = Mid(lines(cursorY), cursorX)
                    lines(cursorY) = before & after
                    cursorX -= 1
                ElseIf cursorY > 1 Then
                    cursorX = Len(lines(cursorY - 1)) + 1
                    lines(cursorY - 1) = lines(cursorY - 1) & lines(cursorY)
                    For i As Integer = cursorY To lineCount - 1
                        lines(i) = lines(i + 1)
                    Next
                    lineCount -= 1
                    cursorY -= 1
                End If
            ElseIf k = Chr(255) & "K" Then
                If cursorX > 1 Then
                    cursorX -= 1
                ElseIf cursorY > 1 Then
                                If run_mode Then
                                    Dim As Integer clicked_ctrl = windows(i)->HitControl(local_x, local_y)
                                    If clicked_ctrl > 0 Then
                                        Dim As tui.uicontrol Ptr c = windows(i)->get_control(clicked_ctrl)
                                        If c <> 0 Then
                                            If c->tool_type = 1 Then
                                                '' Toggle Check Box
                                                c->checked = Not c->checked
                                                windows(1)->show()
                                            ElseIf c->tool_type = 2 Then
                                                '' Combo Box - cycle through items
                                                c->selected_index += 1
                                                If c->selected_index >= c->item_count Then
                                                    c->selected_index = 0
                                                End If
                                                windows(1)->show()
                                            ElseIf c->tool_type = 3 Then
                                                Dim eventName As String = "on_click_" & c->name_id
                                                tui.ExecuteEvent(eventName, windows(1))
                                                windows(1)->show()
                                            ElseIf c->tool_type = 10 Then
                                                '' List Box - select item
                                                Dim As Integer rel_y = local_y - c->y - 1
                                                Dim As Integer item_idx = c->scroll_offset + rel_y
                                                If item_idx >= 0 And item_idx < c->item_count Then
                                                    c->selected_index = item_idx
                                                    windows(1)->show()
                                                End If
                                            ElseIf c->tool_type = 11 Then
                                                '' Option Button - uncheck others in same group
                                                c->checked = 1
                                                For j As Integer = 1 To windows(i)->count
                                                    Dim As tui.uicontrol Ptr other = windows(i)->get_control(j)
                                                    If other <> 0 And other->tool_type = 11 And other <> c Then
                                                        If other->group = c->group Then
                                                            other->checked = 0
                                                        End If
                                                    End If
                                                Next
                                                windows(1)->show()
                                            End If
                                        End If
                                    End If
    '' RUNTIME INTERPRETER
    Function ExtractString(s As String, startPos As Integer) As String
        Dim result As String = ""
        Dim i As Integer = startPos
        If Mid(s, i, 1) <> """" Then Return ""
        i += 1
        While i <= Len(s)
            Dim c As String = Mid(s, i, 1)
            If c = """" Then Exit While
            result &= c
            i += 1
        Wend
        Return result
    End Function

    Function ParsePropertyAccess(expr As String, ByRef ctrlName As String, ByRef propName As String) As Boolean
        Dim dotPos As Integer = InStr(expr, ".")
        If dotPos = 0 Then Return False
        ctrlName = TrimStr(Left(expr, dotPos - 1))
        propName = TrimStr(Mid(expr, dotPos + 1))
        Return True
    End Function

    Sub ExecuteLine(line As String, formWin As window Ptr)
        line = TrimStr(line)
        If Len(line) = 0 Then Return
        If Left(line, 1) = "'" Then Return
        If Left(line, 2) = "''" Then Return
        If Left(LCase(line), 6) = "msgbox" Then
            Dim startQuote As Integer = InStr(line, """"")
            If startQuote > 0 Then
                Dim msg As String = ExtractString(line, startQuote)
                ShowMessageBox(msg, "Message")
            End If
            Return
        End If
        Dim eqPos As Integer = InStr(line, "=")
                                                '' Check for double-click on supported controls to open code editor
                                                If is_double_click And (c->tool_type = 1 Or c->tool_type = 2 Or c->tool_type = 3 Or c->tool_type = 10 Or c->tool_type = 11) Then
                                                    c->code = tui.EditCode(c->name_id, c->code)
                                                    RedrawScreen()
                                                    dragged_ctrl = 0
                                p = 1
                            Else
                                p += 1
                            End If
                        Wend
                        partCount += 1
                        If partCount <= 10 Then
                            parts(partCount) = TrimStr(temp)
                        End If
                        For i As Integer = 1 To partCount
                            Dim part As String = parts(i)
                            If Left(part, 1) = """" Then
                                result &= ExtractString(part, 1)
                            Else
                                Dim cn As String, pn As String
                                If ParsePropertyAccess(part, cn, pn) Then
                                    Dim rc As uicontrol Ptr = formWin->find_control_by_name(cn)
                                    If rc <> 0 And LCase(pn) = "caption" Then
                                        result &= rc->caption
                                    End If
                                End If
                            End If
                        Next
                        If LCase(propName) = "caption" Then
                            c->caption = result
                If Not clicked_handled Then
                    For i As Integer = 2 To 1 Step -1
                        If i = 2 And run_mode Then Continue For
                        If windows(i)->HitTest(mx, my) Then
                            Dim As Integer local_x = mx - windows(i)->x
                            Dim As Integer local_y = my - windows(i)->y
                            If i = 2 Then
                                If clicked_property_row Then
                                    Dim As tui.uicontrol Ptr c = windows(1)->get_control(selected_ctrl_idx)
                                    If local_y = 5 Then editing_prop = 1: edit_buffer = c->name_id
                                    If local_y = 6 Then editing_prop = 2: edit_buffer = c->caption
                                    If local_y = 7 Then editing_prop = 3: edit_buffer = Str(c->x)
                                    If local_y = 8 Then editing_prop = 4: edit_buffer = Str(c->y)
                                    If local_y = 9 Then editing_prop = 5: edit_buffer = Str(c->w)
                                    If local_y = 10 Then editing_prop = 6: edit_buffer = Str(c->h)
                                    redraw_properties = True
                                ElseIf local_y = 12 Then
                                    '' Clicked "Edit Menu" area
                                    windows(1)->edit_menu()
                                    RedrawScreen()
                                Else
                                    dragged_win = i
                                    drag_offset_x = local_x
                                    drag_offset_y = local_y
                                End If
                            Else
                                '' Check if clicked on menu bar
                                If local_y = 1 And windows(i)->menu_count > 0 Then
                                    '' Find which menu item was clicked
                                    Dim As Integer menu_x = 1
                                    For m As Integer = 1 To windows(i)->menu_count
                                        If windows(i)->menu_items(m).parent = 0 Then
                                            Dim As Integer item_w = Len(windows(i)->menu_items(m).caption) + 2
                                            If local_x >= menu_x And local_x < menu_x + item_w Then
                                                '' Found the menu - show it or execute
                                                If run_mode Then
                                                    '' In runtime, execute menu event
                                                    Dim eventName As String = "on_menu_" & windows(i)->menu_items(m).name_id
                                                    tui.ExecuteEvent(eventName, windows(i))
                                                Else
                                                    '' In design mode, edit the menu
                                                    windows(i)->edit_menu()
                                                    RedrawScreen()
                                                End If
                                                clicked_handled = True
                                                Exit For
                                            End If
                                            menu_x += item_w + 2
                                        End If
                                    Next
                                    If clicked_handled Then Exit For
                                End If
                                
                                If run_mode Then
Color 7, 0
Cls

Dim As tui.Toolbox tools = tui.Toolbox(2, 3)
Dim As tui.window Ptr windows(1 To 2)
windows(1) = New tui.window(22, 5, 36, 17, "Form 1")
windows(2) = New tui.window(60, 3, 20, 15, "Properties")

Dim As Integer selected_win_idx = 0
Dim As Integer selected_ctrl_idx = 0
Dim As Integer editing_prop = 0
Dim As String edit_buffer = ""
Dim run_mode As Boolean = False
Dim run_focused_ctrl As Integer = 0

Dim last_click_time As Double = 0
Dim last_click_x As Integer = 0
Dim last_click_y As Integer = 0
Const DOUBLE_CLICK_TIME As Double = 0.4

Color 0, 7
Locate 1, 1: Print " File  Edit  View  Run  Debug  Options"; Space(40);
tools.draw()
For i As Integer = 1 To 2
    windows(i)->show()
Next

Dim As Integer mx = 0, my = 0, mwheel = 0, mbuttons = 0
Dim As Integer old_mx = 0, old_my = 0
Dim As Integer dragged_win = 0, drag_offset_x = 0, drag_offset_y = 0
Dim As Integer dragged_ctrl = 0
Dim As Boolean dragged_tool = False
Dim As Boolean resizing_ctrl = False
Dim As Boolean was_clicked = False
Dim As Boolean redraw_properties = True
Dim As String key_press

Dim As Integer MOUSE_OFFSET_X = 1
Dim As Integer MOUSE_OFFSET_Y = 1

#Macro CommitEdit_Macro
If editing_prop > 0 And selected_win_idx > 0 And selected_ctrl_idx > 0 Then
    Dim As tui.uicontrol Ptr c = windows(selected_win_idx)->get_control(selected_ctrl_idx)
    If c <> 0 Then
        Select Case editing_prop
            Case 1: c->name_id = edit_buffer
            Case 2: c->caption = edit_buffer
            Case 3: c->x = Val(edit_buffer)
            Case 4: c->y = Val(edit_buffer)
            Case 5: c->w = Val(edit_buffer)
            Case 6: c->h = Val(edit_buffer)
        End Select
        If c->w < 4 Then c->w = 4
        If c->tool_type = 3 Then
            If c->h < 3 Then c->h = 3
        Else
            If c->h < 1 Then c->h = 1
        End If
        If c->x < 1 Then c->x = 1
        If c->y < 1 Then c->y = 1
        If c->x + c->w > windows(selected_win_idx)->w - 2 Then c->x = windows(selected_win_idx)->w - c->w - 2
        If c->y + c->h > windows(selected_win_idx)->h - 2 Then c->y = windows(selected_win_idx)->h - c->h - 2
    End If
    windows(selected_win_idx)->show(selected_ctrl_idx)
End If
editing_prop = 0
redraw_properties = True
#EndMacro

Function ShowFileMenu() As Integer
    Dim menuX As Integer = 1
    Dim menuY As Integer = 2
    Dim menuW As Integer = 22
    Dim menuH As Integer = 5
    Color 15, 0
    Locate menuY, menuX
    Print "┌" & tui.RepeatUTF8(menuW - 2, "─") & "┐";
    Locate menuY + 1, menuX
    Print "│ Save Project As...   │";
    Locate menuY + 2, menuX
    Print "│ Load Project...      │";
    Locate menuY + 3, menuX
    Print "│──────────────────────│";
    Locate menuY + 4, menuX
    Print "│ Exit                 │";
    Locate menuY + 5, menuX
    Print "└" & tui.RepeatUTF8(menuW - 2, "─") & "┘";
    Dim sel As Integer = 0
    While sel = 0
        Dim mmx As Integer, mmy As Integer, mmw As Integer, mmb As Integer
        GetMouse mmx, mmy, mmw, mmb
        If mmx <> -1 Then
            mmx += MOUSE_OFFSET_X
            mmy += MOUSE_OFFSET_Y
            If (mmx < menuX Or mmx > menuX + menuW Or mmy < menuY Or mmy > menuY + menuH) And (mmb And 1) Then
                Return 0
            End If
            If (mmb And 1) Then
                If mmx >= menuX And mmx <= menuX + menuW Then
                    If mmy = menuY + 1 Then Return 1
                    If mmy = menuY + 2 Then Return 2
                    If mmy = menuY + 4 Then Return 3
                End If
            End If
        End If
        If Inkey() = Chr(27) Then Return 0
        Sleep 10, 1
    Wend
    Return sel
End Function

Sub RedrawScreen()
    Cls
    If run_mode Then
        Color 0, 7
        Locate 1, 1: Print " File  Edit  View [STOP] Debug  Options"; Space(40);
    Else
        Color 0, 7
        Locate 1, 1: Print " File  Edit  View [RUN ] Debug  Options"; Space(40);
        tools.draw()
        windows(2)->show()
    End If
    windows(1)->show()
End Sub

While 1
    key_press = Inkey()
    If key_press = Chr(27) And Not run_mode Then Exit While
    If key_press = Chr(27) And run_mode Then
        run_mode = False
        run_focused_ctrl = 0
        RedrawScreen()
    End If
    
    If Not run_mode And key_press <> "" Then
        If editing_prop = 0 And selected_win_idx > 0 And selected_ctrl_idx > 0 Then
            If key_press = Chr(8) Or (Len(key_press) = 1 And Asc(key_press) >= 32 And Asc(key_press) <= 126) Then
                Dim As tui.uicontrol Ptr c = windows(selected_win_idx)->get_control(selected_ctrl_idx)
                editing_prop = 2
                edit_buffer = c->caption
            End If
        End If
        If editing_prop > 0 Then
            If key_press = Chr(13) Then
                CommitEdit_Macro
            ElseIf key_press = Chr(8) Then
                If Len(edit_buffer) > 0 Then edit_buffer = Left(edit_buffer, Len(edit_buffer) - 1)
                redraw_properties = True
            ElseIf Len(key_press) = 1 And Asc(key_press) >= 32 And Asc(key_press) <= 126 Then
                If editing_prop >= 3 And (Asc(key_press) < Asc("0") Or Asc(key_press) > Asc("9")) And key_press <> "-" Then
                Else
                    If Len(edit_buffer) < 9 Then edit_buffer &= key_press
                End If
                redraw_properties = True
            End If
        End If
    End If

    GetMouse mx, my, mwheel, mbuttons
    If mx <> -1 Then
        mx += MOUSE_OFFSET_X
        my += MOUSE_OFFSET_Y
        Dim As Boolean mouse_moved = (mx <> old_mx Or my <> old_my)
        Dim As Boolean left_click = (mbuttons And 1) <> 0
        
        If left_click Then
            If was_clicked = False Then
                was_clicked = True
                Dim current_time As Double = Timer
                Dim is_double_click As Boolean = False
                If (current_time - last_click_time < DOUBLE_CLICK_TIME) And (mx = last_click_x And my = last_click_y) Then
                    is_double_click = True
                End If
                last_click_time = current_time
                last_click_x = mx
                last_click_y = my
        If Not run_mode And redraw_properties Then
            Dim As tui.window Ptr prop_win = windows(2)
            Color 8, 7
            For py As Integer = 1 To prop_win->h - 2
                Locate prop_win->y + py, prop_win->x + 1: Print Space(prop_win->w - 2);
            Next
            If selected_win_idx > 0 And selected_ctrl_idx > 0 Then
                Dim As tui.uicontrol Ptr c = windows(selected_win_idx)->get_control(selected_ctrl_idx)
                If c <> 0 Then
                    Locate prop_win->y + 2, prop_win->x + 2: Color 0, 7: Print "Type: " & Trim(tools.items(c->tool_type))
                    Locate prop_win->y + 3, prop_win->x + 1: Color 8, 7: Print tui.RepeatUTF8(prop_win->w - 2, "─")
                    #Macro DrawProp(ly, lbl, p_id, val_str)
                        Locate prop_win->y + ly, prop_win->x + 2
                        Color 0, 7: Print lbl;
                        Locate prop_win->y + ly, prop_win->x + 8
                        Color 0, 3
                        If editing_prop = p_id Then
                            Print Left(edit_buffer & "_         ", 10);
                        Else
                            Print Left(val_str & "          ", 10);
                        End If
                    #EndMacro
                    DrawProp(5, "Name:", 1, c->name_id)
                    DrawProp(6, "Cap: ", 2, c->caption)
                    DrawProp(7, "X:   ", 3, Str(c->x))
                    DrawProp(8, "Y:   ", 4, Str(c->y))
                    DrawProp(9, "W:   ", 5, Str(c->w))
                    DrawProp(10, "H:   ", 6, Str(c->h))
                    Color 0, 7
                End If
            Else
                '' Show form properties including menu
                Locate prop_win->y + 2, prop_win->x + 2: Color 0, 7: Print "Form Properties"
                Locate prop_win->y + 3, prop_win->x + 1: Color 8, 7: Print tui.RepeatUTF8(prop_win->w - 2, "─")
                Locate prop_win->y + 5, prop_win->x + 2: Color 0, 7: Print "Menu items: " & Str(windows(1)->menu_count)
                Locate prop_win->y + 7, prop_win->x + 2: Color 15, 1: Print " Click here to edit menu ";
                Color 0, 7
            End If
            redraw_properties = False
        End If
                        End If
                    ElseIf choice = 3 Then
                        Exit While
                    End If
                    clicked_handled = True
                ElseIf Not run_mode And mx >= tools.x And mx < tools.x + tools.w And my >= tools.y And my < tools.y + tools.h Then
                    If tools.process_click(mx, my) Then
                        tools.draw()
                        Color 15, 0: Locate 1, 60: Print "Selected: " & Trim(tools.items(tools.active_tool)) & Space(10): Color 0, 7
                    Else
                        dragged_tool = True
                        drag_offset_x = mx - tools.x
                        drag_offset_y = mx - tools.y
                    End If
                    clicked_handled = True
                End If
                
                If Not clicked_handled Then
                    For i As Integer = 2 To 1 Step -1
                        If i = 2 And run_mode Then Continue For
                        If windows(i)->HitTest(mx, my) Then
                            Dim As Integer local_x = mx - windows(i)->x
                            Dim As Integer local_y = my - windows(i)->y
                            If i = 2 Then
                                If clicked_property_row Then
                                    Dim As tui.uicontrol Ptr c = windows(1)->get_control(selected_ctrl_idx)
                                    If local_y = 5 Then editing_prop = 1: edit_buffer = c->name_id
                                    If local_y = 6 Then editing_prop = 2: edit_buffer = c->caption
                                    If local_y = 7 Then editing_prop = 3: edit_buffer = Str(c->x)
                                    If local_y = 8 Then editing_prop = 4: edit_buffer = Str(c->y)
                                    If local_y = 9 Then editing_prop = 5: edit_buffer = Str(c->w)
                                    If local_y = 10 Then editing_prop = 6: edit_buffer = Str(c->h)
                                    redraw_properties = True
                                Else
                                    dragged_win = i
                                    drag_offset_x = local_x
                                    drag_offset_y = local_y
                                End If
                            Else
                                If run_mode Then
                                    Dim As Integer clicked_ctrl = windows(i)->HitControl(local_x, local_y)
                                    If clicked_ctrl > 0 Then
                                        Dim As tui.uicontrol Ptr c = windows(i)->get_control(clicked_ctrl)
                                        If c <> 0 Then
                                            If c->tool_type = 1 Then
                                                '' Toggle Check Box
                                                c->checked = Not c->checked
                                                windows(1)->show()
                                            ElseIf c->tool_type = 3 Then
                                                Dim eventName As String = "on_click_" & c->name_id
                                                tui.ExecuteEvent(eventName, windows(1))
                                                windows(1)->show()
                                            ElseIf c->tool_type = 11 Then
                                                '' Option Button - uncheck others in same group
                                                c->checked = 1
                                                For j As Integer = 1 To windows(i)->count
                                                    Dim As tui.uicontrol Ptr other = windows(i)->get_control(j)
                                                    If other <> 0 And other->tool_type = 11 And other <> c Then
                                                        If other->group = c->group Then
                                                            other->checked = 0
                                                        End If
                                                    End If
                                                Next
                                                windows(1)->show()
                                            End If
                                        End If
                                    End If
                                Else
                                    If tools.active_tool = 0 Then
                                        Dim As Boolean matched_control = False
                                        If selected_win_idx = i And selected_ctrl_idx > 0 Then
                                            Dim As tui.uicontrol Ptr c = windows(i)->get_control(selected_ctrl_idx)
                                            If c <> 0 Then
                                                If local_x = c->x + c->w And local_y = c->y + c->h Then
                                                    resizing_ctrl = True
                                                    dragged_ctrl = selected_ctrl_idx
                                                    matched_control = True
                                                End If
                                            End If
                                        End If
                                        If Not matched_control Then
                                            Dim As Integer clicked_ctrl = windows(i)->HitControl(local_x, local_y)
                                            If clicked_ctrl > 0 Then
                                                selected_win_idx = i
                                                selected_ctrl_idx = clicked_ctrl
                                                dragged_ctrl = clicked_ctrl
                                                
                                                Dim As tui.uicontrol Ptr c = windows(i)->get_control(clicked_ctrl)
                                                drag_offset_x = local_x - c->x
                                                drag_offset_y = local_y - c->y
                                                
                                                '' Check for double-click on supported controls to open code editor
                                                If is_double_click And (c->tool_type = 1 Or c->tool_type = 3 Or c->tool_type = 11) Then
                                                    c->code = tui.EditCode(c->name_id, c->code)
                                                    RedrawScreen()
                                                    dragged_ctrl = 0
                                                Else
                                                    windows(i)->show(selected_ctrl_idx)
                                                    redraw_properties = True
                                                End If
                                                matched_control = True
                                            End If
                                        End If
                                        If Not matched_control Then
                                            dragged_win = i
                                            drag_offset_x = local_x
                                            drag_offset_y = local_y
                                            selected_ctrl_idx = 0
                                            windows(i)->show()
                                            redraw_properties = True
                                        End If
                                    Else
                                        '' Place control with parent frame detection
                                        If local_x > 0 And local_x < windows(i)->w - 14 And local_y > 0 And local_y < windows(i)->h - 1 Then
                                            windows(i)->add_control(local_x, local_y, tools.active_tool, tools.items(tools.active_tool))
                                            selected_win_idx = i
                                            selected_ctrl_idx = windows(i)->count
                                            
                                            '' Check if dropped inside a frame
                                            Dim As tui.uicontrol Ptr new_ctrl = windows(i)->get_control(selected_ctrl_idx)
                                            If new_ctrl <> 0 And new_ctrl->tool_type <> 7 Then
                                                For j As Integer = windows(i)->count - 1 To 1 Step -1
                                                    Dim As tui.uicontrol Ptr potential_parent = windows(i)->get_control(j)
                                                    If potential_parent <> 0 And potential_parent->tool_type = 7 Then
                                                        '' Check if new control is inside this frame
                                                        If new_ctrl->x >= potential_parent->x + 1 And _
                                                           new_ctrl->x + new_ctrl->w <= potential_parent->x + potential_parent->w - 1 And _
                                                           new_ctrl->y >= potential_parent->y + 1 And _
                                                           new_ctrl->y + new_ctrl->h <= potential_parent->y + potential_parent->h - 1 Then
                                                            new_ctrl->parent = j
                                                            Exit For
                                                        End If
                                                    End If
                                                Next
                                            End If
                                            
                                            redraw_properties = True
                                            tools.active_tool = 0
                                            tools.draw()
                                            windows(i)->show(selected_ctrl_idx)
                                        End If
                                    End If
                                End If
                            End If
                            Exit For
                        End If
                    Next
                End If
            End If
            
            If Not run_mode And mouse_moved Then
                If resizing_ctrl And dragged_ctrl > 0 Then
                    Dim As tui.uicontrol Ptr c = windows(selected_win_idx)->get_control(dragged_ctrl)
                    Dim As Integer new_w = (mx - windows(selected_win_idx)->x) - c->x
                    Dim As Integer new_h = (my - windows(selected_win_idx)->y) - c->y
                    If new_w < 4 Then new_w = 4
                    If c->tool_type = 3 Then
                        If new_h < 3 Then new_h = 3
                    Else
                        If new_h < 1 Then new_h = 1
                    End If
                    If c->x + new_w > windows(selected_win_idx)->w - 2 Then new_w = windows(selected_win_idx)->w - c->x - 2
                    If c->y + new_h > windows(selected_win_idx)->h - 2 Then new_h = windows(selected_win_idx)->h - c->y - 2
                    c->w = new_w
                    c->h = new_h
                    redraw_properties = True
                    windows(selected_win_idx)->show(selected_ctrl_idx)
                ElseIf dragged_ctrl > 0 Then
                    Dim As tui.uicontrol Ptr c = windows(selected_win_idx)->get_control(dragged_ctrl)
                    Dim As Integer new_x = (mx - windows(selected_win_idx)->x) - drag_offset_x
                    Dim As Integer new_y = (my - windows(selected_win_idx)->y) - drag_offset_y
                    If new_x > 0 And new_y > 0 And new_x + c->w < windows(selected_win_idx)->w - 1 And new_y + c->h < windows(selected_win_idx)->h - 1 Then
                        c->x = new_x
                        c->y = new_y
                        redraw_properties = True
                    End If
                    windows(selected_win_idx)->show(selected_ctrl_idx)
                ElseIf dragged_tool Then
                    tools.remove()
                    tools.x = mx - drag_offset_x
                    tools.y = my - drag_offset_y
                    If tools.x < 1 Then tools.x = 1
                    If tools.y < 2 Then tools.y = 2
                    If tools.x + tools.w > 80 Then tools.x = 80 - tools.w + 1
                    If tools.y + tools.h > 25 Then tools.y = 25 - tools.h + 1
                    For i As Integer = 1 To 2
                        If selected_win_idx = i Then
                            windows(i)->show(selected_ctrl_idx)
                        Else
                            windows(i)->show()
                        End If
                    Next
                    tools.draw()
                ElseIf dragged_win > 0 Then
                    windows(dragged_win)->x = mx - drag_offset_x
                    windows(dragged_win)->y = my - drag_offset_y
                    tools.draw()
                    For i As Integer = 1 To 2
                        If i <> dragged_win Then
                            If selected_win_idx = i Then
                                windows(i)->show(selected_ctrl_idx)
                            Else
                                windows(i)->show()
                            End If
                        End If
                    Next
                    If selected_win_idx = dragged_win Then
                        windows(dragged_win)->show(selected_ctrl_idx)
                    Else
                        windows(dragged_win)->show()
                    End If
                End If
            End If
        Else
            was_clicked = False
            dragged_win = 0
            dragged_ctrl = 0
            dragged_tool = False
            resizing_ctrl = False
        End If

        If Not run_mode And redraw_properties Then
            Dim As tui.window Ptr prop_win = windows(2)
            Color 8, 7
            For py As Integer = 1 To prop_win->h - 2
                Locate prop_win->y + py, prop_win->x + 1: Print Space(prop_win->w - 2);
            Next
            If selected_win_idx > 0 And selected_ctrl_idx > 0 Then
                Dim As tui.uicontrol Ptr c = windows(selected_win_idx)->get_control(selected_ctrl_idx)
                If c <> 0 Then
                    Locate prop_win->y + 2, prop_win->x + 2: Color 0, 7: Print "Type: " & Trim(tools.items(c->tool_type))
                    Locate prop_win->y + 3, prop_win->x + 1: Color 8, 7: Print tui.RepeatUTF8(prop_win->w - 2, "─")
                    #Macro DrawProp(ly, lbl, p_id, val_str)
                        Locate prop_win->y + ly, prop_win->x + 2
                        Color 0, 7: Print lbl;
                        Locate prop_win->y + ly, prop_win->x + 8
                        Color 0, 3
                        If editing_prop = p_id Then
                            Print Left(edit_buffer & "_         ", 10);
                        Else
                            Print Left(val_str & "          ", 10);
                        End If
                    #EndMacro
                    DrawProp(5, "Name:", 1, c->name_id)
                    DrawProp(6, "Cap: ", 2, c->caption)
                    DrawProp(7, "X:   ", 3, Str(c->x))
                    DrawProp(8, "Y:   ", 4, Str(c->y))
                    DrawProp(9, "W:   ", 5, Str(c->w))
                    DrawProp(10, "H:   ", 6, Str(c->h))
                    Color 0, 7
                End If
            Else
                Locate prop_win->y + 2, prop_win->x + 2: Color 0, 7: Print "No selection."
            End If
            redraw_properties = False
        End If

        If mouse_moved Then
            old_mx = mx
            old_my = my
        End If
        If mx >= 1 And mx <= 80 And my >= 1 And my <= 25 Then
            Locate my, mx, 1
        End If
    End If
    Sleep 10, 1
Wend

For i As Integer = 1 To 2
    Delete windows(i)
Next
Color 7, 0
Cls
